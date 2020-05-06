"""
	Ah yes, the minion that quietly does it's work whenever called. This little bad boy of ours can crunch data and saves them
	to our data/ directory. It also does the magic of inserting stuff into HTML

	Minion's daily motivation:
		This youtube video explaining the beauty of life. This video, according to the minion, captures the essence
		of life, the universe and everything. The minion believes that this video is fundamental to the universe just as you and I are made
		up of atoms. As you can see, this video is everything to the minion. Please make sure that YouTube never takes it down because if
		YouTube was going to let us down, I don't know what minion would do:
		https://www.youtube.com/watch?v=dQw4w9WgXcQ

	Author: IceCereal + achal.ochod
"""

import copy
import gspread
from json import dump, load
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Yes, the minion has it's own slaves to work.
# I, Cereal God, urge you to go through their code and see their interests.
# #SlavesLivesMattersAndSoDoTheirInterests

from BigDataBox.utils.website.history.testing import testing as history_testing
from BigDataBox.utils.website.history.infected_daily import infected_daily as history_infected_daily
from BigDataBox.utils.website.history.states_infected import states_infected as history_states_infected
from BigDataBox.utils.website.history.district_values import district_values as history_district_values
from BigDataBox.utils.website.history.twenty_four_hours import twenty_four_hours as history_twenty_four_hours

from BigDataBox.utils.website.present.zones import zones as present_zones
from BigDataBox.utils.website.present.states_infected import states_infected as present_states_infected
from BigDataBox.utils.website.present.district_values import district_values as present_district_values
from BigDataBox.utils.website.present.states_cases_deaths import states_cases_deaths as present_states_cases_deaths
from BigDataBox.utils.website.present.cured_tested_values import cured_tested_values as present_cured_tested_values

from BigDataBox.utils.website.general.general import general
from BigDataBox.utils.website.latest_updates.latest_updates import latest_updates_V2
from BigDataBox.utils.website.csv.history.states_infected import states_infected as csv_history_states_infected


#####################
# PUBLIC API IS ON A HOLD UNTIL IT CAN BE FIGURED OUT WHAT TO BE DONE
#####################

# # Raw-Data
# from BigDataBox.utils.public.covindia.raw_data import raw_data
# # Present-State-Data
# from BigDataBox.utils.public.covindia.state_data import state_data
# # Present-General-Data
# from BigDataBox.utils.public.covindia.general_data import general_data
# # History-District-Data
# from BigDataBox.utils.public.covindia.district_date_data import district_date_data

#####################
# PUBLIC API ENDS
#####################

# Directories
DIR_DATA = "../data/"
DIR_RES = "res/"
DIR_PRODUCTION = "live/"
DIR_TESTS = "tests/"

def do_your_work(testing : bool = None):
	"""
		Get the damn data from our google sheet and crunch these numbers.
		Store the numbers in your DIR_DATA, slave.
	"""

	if testing:
		data_old = []
		data_new = []
		data_cured = []
		data_testing = []

		import csv

		with open(DIR_TESTS + "sheet_old.csv", 'r') as F:
			reader = csv.reader(F)
			for row in reader:
				data_old.append(row)

		with open(DIR_TESTS + "sheet_new.csv", 'r') as F:
			reader = csv.reader(F)
			for row in reader:
				data_new.append(row)

		with open(DIR_TESTS + "sheet_cured.csv", 'r') as F:
			reader = csv.reader(F)
			for row in reader:
				data_cured.append(row)

		with open(DIR_TESTS + "sheet_testing.csv", 'r') as F:
			reader = csv.reader(F)
			for row in reader:
				data_testing.append(row)

	else:
		scope = ['https://spreadsheets.google.com/feeds']
		creds = ServiceAccountCredentials.from_json_keyfile_name(DIR_RES + 'creds.json',scope)
		client = gspread.authorize(creds)
		with open(DIR_RES + "URLS.json", 'r') as F:
			urls = load(F)
		sheet_old = client.open_by_url(urls['Old-Sheet']).worksheet('Sheet1')
		sheet_new = client.open_by_url(urls['New-Sheet']).worksheet('Sheet1')
		sheet_cured = client.open_by_url(urls['Cured']).worksheet('Sheet1')
		sheet_testing = client.open_by_url(urls['Testing']).worksheet('Sheet1')

		print ("Pinging Sheets...")
		data_old = sheet_old.get()
		data_new = sheet_new.get()
		data_cured = sheet_cured.get()
		data_testing = sheet_testing.get()
	
	# Remove Headers
	data_old = data_old[1:]
	data_new = data_new[1:]
	data_cured = data_cured[1:]
	data_testing = data_testing[1:]

	FAILLIST = []

	# OTHERS
	print ("Computing general...")
	DATA_general = general(data_new, data_cured, testing)

	print ("Computing latest-updates...")
	flag, failList = latest_updates_V2(data_new, 5, testing)

	print("Computing csv-history-states-infected...")
	flag, failList = csv_history_states_infected(data_old, testing)


	### HISTORY
	print("Computing history-testing...")
	history_testing(data_testing, testing)

	print ("Computing history-twenty-four-hours...")
	history_twenty_four_hours(data_new, testing)

	print ("Computing history-infected-daily...")
	dataCopy = copy.deepcopy(data_old)
	flag, failList = history_infected_daily(dataCopy, testing)

	print ("Computing history-states-infected...")
	flag, failList = history_states_infected(data_old, testing)

	print ("Computing history-districts-values...")
	dataCopy = copy.deepcopy(data_new)
	flag, failList = history_district_values(dataCopy, testing)


	### PRESENT
	print ("Computing present-zones...")
	present_zones(testing)

	print("Computing present-cured-tested-values...")
	present_cured_tested_values(data_cured, testing)

	print ("Computing present-states-infected...")
	flag, failList = present_states_infected(data_new, testing)

	print ("Computing present-states-cases-deaths...")
	flag, failList = present_states_cases_deaths(data_new, testing)

	print ("Computing present-district-values...")
	flag, failList = present_district_values(DATA_general, testing)


	#####################
	# PUBLIC API IS ON A HOLD UNTIL IT CAN BE FIGURED OUT WHAT TO BE DONE
	#####################

	# print ("\nPublic:")
	# print ("Computing covindia-raw-data...")
	# raw_data(data, testing)

	# print ("Computing covindia-present-state-data...")
	# state_data(data, testing)

	# print ("Computing covindia-present-general-data...")
	# general_data(data, testing)

	# print ("Computing covindia-history-district-data...")
	# dataCopy = copy.deepcopy(data)
	# district_date_data(dataCopy, testing)

	#####################
	# PUBLIC API ENDS HERE
	#####################

	print ("\nFaillist:", FAILLIST)
	# TODO: Handle faillist and send it to overlord

if __name__ == "__main__":
	do_your_work()
