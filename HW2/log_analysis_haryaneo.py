#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: NiroHaryamen
# @Date:   2015-01-22 00:34:48
# @Last Modified by:   NiroHaryamen
# @Last Modified time: 2015-01-27 11:23:42

import re
import urlparse
import time
import calendar
from itertools import groupby
import csv

#Check if the query has the length <= 255
def valid_query(request):
	MAX_NUMBER_OF_CHARACTERS = 255
	parse_string = urlparse.urlparse(request['URL'])[4]
	decoded_query = urlparse.parse_qs(parse_string)
	for key in decoded_query:
		if len(decoded_query[key][0]) > MAX_NUMBER_OF_CHARACTERS:
			return False
	return True


def valid_domain(request):

	pattern = r'([A-z]+)\.([A-z\d]+)'
	# pattern = r'([A-Za-z]+)|([A-za-z]+)'
	# pattern = r'([A-z]+)\.([A-z\d]+)|([A-z\d]+)\.([A-z]+)'
	parse_string = urlparse.urlparse(request['URL'])[1]
	# print parse_string
	match = re.findall(pattern,parse_string,re.IGNORECASE)
	if len(match) > 0:
		result = True
	else:
		result = False

	# print request['URL'], result
	# print parse_string, result
	return result

#Check if the protocol is valid
def valid_protocol(request):
	# # pattern = r'(http://[A-Za-z])|(https://[A-Za-z])|(HTTP://[A-Za-z])|(HTTPS://[A-Za-z])'
	parse_string = urlparse.urlparse(request['URL'])[0]

	# print parse_string
	pattern = r'http|https'
	valid = re.findall(pattern,parse_string,re.IGNORECASE)
	if valid:
		result = True
	else:
		result = False
	# print parse_string, result
	return result

#Check if the status is valid
def valid_status(request): #correct
	if request['Status'] == 200:
		result = True
	else:
		result = False
	# print request['Status'], result
	return result

def valid_method(request): #correct
	if request['Method'].upper() == 'GET' or request['Method'].upper() =='POST':
		result = True
	else:
		result = False
	# print request['Method'], result
	return result

def is_valid(raw_data):
	method = valid_method(raw_data)
	status = valid_status(raw_data)
	protocol = valid_protocol(raw_data)
	domain = valid_domain(raw_data)
	query_length = valid_query(raw_data)
	return method and status and protocol and domain and query_length

def check_and_valid_data(raw_data):
	for line in raw_data:
		line['Valid'] = is_valid(line)
	return raw_data

#Get method and URL
def get_method_url(raw_data): #correct
	# result = re.findall(r'"([^"]*)',raw_data)[0].split()
	result = re.findall(r'"([^"]+)',raw_data,re.IGNORECASE)[0].split()
	# print result
	if len(result) == 1:
		result = ['',str(result).strip('[]')] #strip inner list
	# print result
	return result

#Get Status
def get_status(raw_data): #correct
	result = re.findall(r'" (\d+)',raw_data)[0]
	# print int(result)
	return int(result)

#Get date
def get_date(raw_data): #correct
	result = re.findall(r'\[([^"]*)\]',raw_data)[0]
	temp_result = result.split(':')[0].split('/')
	temp_result.reverse()
	# print '-'.join(temp_result)
	return '-'.join(temp_result)

#Get Date and Time
def get_datetime(raw_data): #correct
	result = re.findall(r'\[([^"]*)\]',raw_data)[0]
	return result

#Get the top level domain
def get_top_level_domain(request):
	url = request['URL'].lower()
	url_parse = urlparse.urlparse(url)
	netloc = ''
	if url_parse[1]:
		netloc = url_parse[1]
		# print netloc
	elif url_parse[2]:
		netloc = url_parse[2]
		# print netloc
	tld = netloc.split('.')[-1].split(':')[0]
	if tld.isalpha():
		return tld
	return ''

#Store raw data into a list of dictionaries
def store_data():
	raw_data = read_file('access_log.txt')
	data_structure = []
	for row in raw_data:
		data_structure.append({'Source':row,'Date':get_date(row),'Datetime':get_datetime(row),'Method':get_method_url(row)[0],'Status':get_status(row),'URL':get_method_url(row)[1]})
	return data_structure

#change date to seconds for sorting valid requests
def get_epoch_date(request):
	time_epoch = time.strptime(request['Date'], "%Y-%b-%d")
	return calendar.timegm(time_epoch)

#change date to seconds for sorting invalid requests
def get_epoch_datetime(request):
	time_epoch = time.strptime(request['Datetime'].split(' ')[0], "%d/%b/%Y:%H:%M:%S")
	return calendar.timegm(time_epoch)



#Append additional data into dictionaries
def add_extra_data(data):
	for request in data:
		request['TLD'] = get_top_level_domain(request)	
		request['Epoch Date'] = get_epoch_date(request)	
		request['Epoch Datetime'] = get_epoch_datetime(request)	
	return data

#Write the headers for valid output
def get_valid_output_headers(valid_requests):
	tlds = []
	for request in valid_requests:
		tlds.append(request['TLD'])
	unique_tlds = list(set(tlds)) #List of unique top level domain
	unique_tlds.sort()
	header = ['date'] + unique_tlds
	return header

#Count the number of valid tld
def get_frequency(date_group, headers):
	frequency_data = []
	for tld in headers[1:]:
		frequency_data.append(len([i for i in date_group if i['TLD'] == tld]))
	return frequency_data


def handle_valid_requests(data):
	# get valid requests
	valid_requests = []
	for req in data:
		if req['Valid']:
			valid_requests.append(req)

	# group data by date
	headers = get_valid_output_headers(valid_requests)
	output_data = []
	valid_requests = sorted(valid_requests, key = lambda x: x['Epoch Date'])
	for key,group in groupby(valid_requests, lambda x: x['Epoch Date']):
		date_group = [i for i in group]
		date_data = date_group[0]['Date']
		freq_data = get_frequency(date_group, headers)
		output_data.append([date_data] + freq_data)

	# Write data into txt file
	with open('valid_log_summary_haryaneo.txt', 'wb') as csvfile:
		writer = csv.writer(csvfile, delimiter='\t')
		writer.writerow(headers)
		for row in output_data:
			writer.writerow(row)
	return

def handle_invalid_requests(data):
	# get invalid requests
	invalid_requests = []
	for req in data:
		if not req['Valid']:
			invalid_requests.append(req)
	invalid_requests = sorted(invalid_requests, key = lambda x: x['Epoch Datetime'])

	# write invalid requests to file
	with open('invalid_access_log_haryaneo.txt','w') as fs:
		for invalid_request in invalid_requests:
			fs.writelines(invalid_request['Source'])
	return

def read_file(filename):
	file_data = []
	input_file = open(filename, 'rU')
	for line in input_file:
		file_data.append(line)
	return file_data

def main():
	raw_data = store_data()
	valid_data = check_and_valid_data(raw_data)
	processed_data = add_extra_data(valid_data)
	handle_valid_requests(processed_data)
	handle_invalid_requests(processed_data)
	return

if __name__== '__main__':
	main()