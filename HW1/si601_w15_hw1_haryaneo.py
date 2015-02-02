#Name: Niro Haryamen Mohd Rais
#UMID: 44257518
#SI601 Winter 2015 HW 1

import math
import csv
import itertools

COUNTRY_NAME_INDEX = 0
TOTAL_POPULATION_INDEX = 9
URBAN_POPULATION_INDEX = 10
BIRTH_RATE_INDEX = 11
STARTING_DATA_ROW = 1

REGION_INDEX = 0
SUB_REGION_INDEX = 1
COUNTRY_INDEX = 2

#Below are the codes for Problem/Step 1
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#This function convert the data from string to integer
def convert_int(string_int):
	if string_int.replace('"','') == '': #return false if the column is empty
		return False
	else:
		return int(string_int.replace(',','').replace('"',''))
		
#This function store the raw data for the 4 columns: 
#country name, total population, urban population, and birth rate population into a list of dictionaries
def store_raw_data():
	file_data = read_file('world_bank_indicators.txt')
	data_structure = []
	for item in file_data[STARTING_DATA_ROW:]: #Append data for all 4 columns into a list of dictionaries
		# defined three new variables that convert the data in 3 different columns into integer
		total_population = convert_int(item[TOTAL_POPULATION_INDEX])
		urban_population = convert_int(item[URBAN_POPULATION_INDEX])
		birth_rate = convert_int(item[BIRTH_RATE_INDEX])/1000.0
		#Append data into a list of dictionaries if the columns are not empty
		if item[COUNTRY_NAME_INDEX]	 and total_population != False and urban_population != False and birth_rate != False :
			data_structure.append({'Country Name':item[COUNTRY_NAME_INDEX],'Total Population':total_population,
				'Urban Population':urban_population,'Birth Rate':birth_rate})
	return data_structure

#This function calculates the average value of data in each column 
#given the data and dictionary key
def calculate_average(country_data, dict_key):
	population_data = [row[dict_key] for row in country_data] 	# get column element using dict_key from country_data
	return sum(population_data)/(len(population_data)*1.0) # formula for average (float)

#This function returns the average total population for every country
def get_average_total_pop(country_data):
	return calculate_average(country_data, 'Total Population')

#This function returns the average urban population for every country
def get_average_urban_pop(country_data):
	return calculate_average(country_data, 'Urban Population')

#This function returns the average birth rate for every country
def get_average_birth_rate(country_data):
	return calculate_average(country_data, 'Birth Rate')

#This function returns the average urban population ratio for every country
def add_average_urban_pop_ratio(average_data):
	for row in average_data: #Append Average Urban Population ratio column for every country
		row['Average Urban Population Ratio'] = row['Average Urban Population'] / row['Average Total Population']*1.0
	return average_data

#This function returns the average birth rate per person for every country
def add_average_birth_rate_per_person(average_data):
	for row in average_data:
		row['Average Log Birth Rate'] = math.log(row['Average Birth Rate'])*-1
	return average_data

#This function takes the raw data, store them in a set of list of countries and compute the average value
#of total population, average urban population and average birth rate population
def store_average_data():
	raw_data = store_raw_data()
	countries = set([row['Country Name'] for row in raw_data]) #make a new set of list of country name
	average_data_structure = [] #empty list for the average data 
	for country in countries:
		country_data = [row for row in raw_data if row['Country Name'] == country] #list of countries data in dictionaries
		
		average_total_pop = get_average_total_pop(country_data) #returns average total population
		average_urban_pop = get_average_urban_pop(country_data)	#returns average urban population
		average_birth_rate = get_average_birth_rate(country_data) #returns average birth rate
		#Append 4 dictionaries to the list
		average_data_structure.append({'Country Name': country, 'Average Total Population': average_total_pop,
		'Average Urban Population': average_urban_pop, 'Average Birth Rate':average_birth_rate})
	return average_data_structure

#This function sorts the average_data by Average Urban Population Ratio and Average Birth Rate
def sort_descending(average_data):
	return sorted(average_data, key = lambda x: (-x['Average Urban Population Ratio'], x['Average Birth Rate']))

#This function writes the output for step 1 in a csv file
def write_to_csv(filename, data):
	with open(filename, 'wb') as fs:
		csv_writer = csv.writer(fs, delimiter=',')
		#This is the header of each column
		csv_writer.writerow(['country name', 'average population', 'average urban population', 
		'average urban population ratio', 'average birth rate'])
		#Write all rows in average_data into csv file 
		for row in data:
			csv_writer.writerow([row['Country Name'], row['Average Total Population'], row['Average Urban Population'], 
			row['Average Urban Population Ratio'], row['Average Log Birth Rate']])
	return 


#Below are the codes for Problem / Step 2
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#This function reads and store the data from world bank regions into a list of dictionaries
def store_regions_data():
	file_data = read_file('world_bank_regions.txt') #read the txt file
	region_data_structure = [] #Create an empty list to store the data
	#Append all the data in world bank regions into a list of dictionaries
	for item in file_data[STARTING_DATA_ROW:]: 
		region_data_structure.append({'Regions':item[REGION_INDEX],'Sub-Region':item[SUB_REGION_INDEX],
		'Country Name':item[COUNTRY_INDEX].replace('\n','')}) #replace the new line with empty string
	return region_data_structure

#This function append the region column to previous average data
def append_regions_to_average_data(average_data,regions_data):
	for item in average_data:
		for regions in regions_data:
			if item['Country Name'] == regions['Country Name']:
				item['Regions'] = regions['Regions']
		if 'Regions' not in item: #print 'No Region' to empty column of region
			item['Regions'] = 'No Region'
	return average_data

#This function writes the output for step 2 in a csv file
def write_to_csv2(filename,data):
	with open(filename, 'wb') as fs:
		csv_writer = csv.writer(fs, delimiter=',')
		#This is the header for each column
		csv_writer.writerow(['country name', 'region', 'average population', 'average urban population', 
		'average urban population ratio', 'average birth rate'])
		#Write all rows in average_data_with_regions into csv file 
		for row in data:
			csv_writer.writerow([row['Country Name'], row['Regions'], row['Average Total Population'], 
			row['Average Urban Population'], row['Average Urban Population Ratio'], row['Average Log Birth Rate']])
	return

#Below are the codes for Problem / Step 3
#xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
#This function returns the highest population country for each region
def get_highest_population(data):
	highest_population_structure = [] #Create an empty list
	data = sorted(data, key = lambda x: x['Regions']) #sort the average_data_with_regions
	for key, group in itertools.groupby(data, key = lambda x: x['Regions']): #Group  the data by regions
		# print 'key', key
		highest_ATP = {'Average Total Population': 0}
		for country in group:
			if country['Average Total Population'] > highest_ATP['Average Total Population']:
				highest_ATP = country
		if key != 'No Region': #Don't include 'No region' into data structure
			highest_population_structure.append({'Regions': key, 'Country': highest_ATP['Country Name']})
	return highest_population_structure

#This function writes the output for step 3 in a csv file
def write_to_csv3(filename,data):
	with open(filename, 'wb') as fs:
		csv_writer = csv.writer(fs, delimiter=',')
		#This is the header for each column
		csv_writer.writerow(['region', 'country with highest average population'])
		#Write all rows in average_data_with_regions into csv file 
		for row in data:
			csv_writer.writerow([row['Regions'], row['Country']])
	return

#This function open, read the filename, and then put all the data into a list
def read_file(filename):
	file_data = []
	input_file = open(filename, 'rU')
	for row in input_file:
		file_data.append(row.split('\t'))
	return file_data


#This is the main function that calls all the other functions 
def main():
	raw_data = store_raw_data()
	#Average data is updated every time functions are called
	average_data = store_average_data()
	average_data = add_average_urban_pop_ratio(average_data)
	average_data = add_average_birth_rate_per_person(average_data)
	average_data = sort_descending(average_data)
	write_to_csv('SI601_HW1_step1_haryaneo.csv', average_data)

	regions_data = store_regions_data()
	average_data_with_regions = append_regions_to_average_data(average_data, regions_data) 
	write_to_csv2('SI601_HW1_step2_haryaneo.csv', average_data_with_regions)

	itertools_data = get_highest_population(average_data_with_regions)
	write_to_csv3('SI601_HW1_step3_haryaneo.csv', itertools_data)

if __name__ == '__main__':
  main()
