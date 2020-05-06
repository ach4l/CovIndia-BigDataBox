"""
	Author: Srikar
"""

import csv
from datetime import datetime

DIR_DATA = "../data/"

def states_infected(data_old, testing : bool = None):

	"""
		API to make an ordered csv of our data for cool visualisations
		uses the data from the sheets directy to make the csv

		Function returns (status, list_of_error)
		1 = All good
		-1 = Something died

		TODO : Optimise the function
	"""

	data_old.sort(key = lambda x: datetime.strptime(x[0], '%d/%m/%Y'))

	csvData = {}
	stateList = []

	dateWriter = ['States']  # For the first row
	writeData = []           # For the rest of the data

	# I'm pretty sure there's a more optimised version of doing this with  a smaller O(), smh I'm a noob

	for row in data_old:

		date = row[0]
		state = row[2]

		if(date not in csvData):
			csvData[date] = {}
		
		if(state not in stateList):
			stateList.append(state)
	data_old = data_old[1:]
	for date in csvData:

		dateWriter.append(date)

		for state in stateList:

			csvData[date][state] = {}

			csvData[date][state]["infected"] = 0
			csvData[date][state]["dead"] = 0


	for row in data_old:

		date = row[0]
		state = row[2]

		if date in csvData:
			if state in csvData[date]:
				
				try:
					csvData[date][state]["infected"] += int(row[4])
				except:
					pass

				try:
					csvData[date][state]["dead"] += int(row[5])
				except:
					pass


	for state in stateList:
		isFirst = True
		sum = 0
		for date in csvData:
			if(isFirst):
				stateArray = [state]
				isFirst = not isFirst
			sum += csvData[date][state]["infected"]
			stateArray.append(sum)
		writeData.append(stateArray)

	if not testing:

		with open(DIR_DATA + 'APIData/csv_history_states_infected.csv', 'w') as csvfile:

			csvwriter = csv.writer(csvfile)  
			
			csvwriter.writerow(dateWriter) # writes the fisrt row, i.e, the dates
			
			csvwriter.writerows(writeData) # Writes the rest of the data
	
	return(1, None)