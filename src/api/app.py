import flask
from flask import jsonify, request, escape, send_file
from json import load, dump
from datetime import datetime
import os

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import gspread
from oauth2client.service_account import ServiceAccountCredentials

DIR_DATA = os.environ['DATA_REPO_PATH']

# Set the connection between GSheets and this server

app = flask.Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
limiter = Limiter(
	app,
	key_func=get_remote_address
)

@app.route('/', methods=['GET'])
def home():
	return "<a href=\"https://covindia.com\">Click here to go to https://covindia.com</a>. You were not supposed to stumble here.<br><br>But now that you did, hello from us!"


########################
####### GENERAL ########
########################
@app.route('/general', methods=['GET'])
def general():
	data = {}
	with open(DIR_DATA + "/APIData/index_general.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/latest-updates', methods=['GET'])
def latest_updates():
	data = {}
	with open(DIR_DATA + "/APIData/latest_updates.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/csv-history-states-infected', methods=['GET'])
def csv_history_states_infected():
	return send_file(DIR_DATA + '/APIData/csv_history_states_infected.csv', mimetype='text/csv',
		attachment_filename='covindia_history_states_infected.csv', as_attachment=True)

@app.route('/table-data', methods=['GET'])
def table_data():
	# A mix of daily_states_complete and cured_data
	tDATA = {}
	curedDATA = {}
	with open(DIR_DATA + "/APIData/present_states_cases_deaths.json", 'r') as FPtr:
		tDATA = load(FPtr)
	with open(DIR_DATA + "/APIData/cured.json", 'r') as FPtr:
		curedDATA = load(FPtr)
	for state in curedDATA:
		try:
			tDATA[state].update(curedDATA[state])
		except:
			# In the random event that curedData has a value that tDATA does not
			tDATA[state] = curedDATA[state]
	return jsonify(tDATA)


########################
####### HISTORY ########
########################
@app.route('/history-infected-daily', methods=['GET'])
def history_infected_daily():
	data = {}
	with open(DIR_DATA + "/APIData/history_infected_daily.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/history-states-infected', methods=['GET'])
def history_states_infected():
	data = {}
	with open(DIR_DATA + "/APIData/history_states_infected.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/history-twenty-four-hours', methods=['GET'])
def history_twenty_four_hours():
	data = {}
	with open(DIR_DATA + "/APIData/history_twenty_four_hours.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/history-testing', methods=['GET'])
def history_testing():
	data = {}
	with open(DIR_DATA + "/APIData/history_testing.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/history-district-values', methods=['GET'])
def history_district_values():
	data = {}
	with open(DIR_DATA + "/APIData/history_district_values.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)


########################
####### PRESENT ########
########################
@app.route('/present-district-values', methods=['GET'])
def present_district_values():
	data = {}
	with open(DIR_DATA + "/APIData/present_district_values.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/present-states-infected', methods=['GET'])
def present_states_infected():
	data = {}
	with open(DIR_DATA + "/APIData/present_states_infected.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/present-cured-tested-values', methods=['GET'])
def present_cured_tested_values():
	data = {}
	with open(DIR_DATA + "/APIData/present_cured_tested_values.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/present-zones', methods=['GET'])
def present_zones():
	data = {}
	with open(DIR_DATA + "/APIData/present_zones.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)

@app.route('/present-states-cases-deaths', methods=['GET'])
def present_states_cases_deaths():
	data = {}
	with open(DIR_DATA + "/APIData/present_states_cases_deaths.json", 'r') as FPtr:
		data = load(FPtr)
	return jsonify(data)


########################
######## OTHER #########
########################
@app.route('/report-numbers', methods=['GET', 'POST'])
@limiter.limit("1 per 10 seconds")
def report_numbers():
	try:
		if request.method == 'POST':
			formData = {}
			compusloryFields = ['state', 'district', 'infected', 'death', 'number', 'date', 'source']
			optionalFields = ['name']

			for field in compusloryFields:
				if request.form[field] == "":
					return jsonify({"success" : False, "message" : "Could not retrieve " + field})
				formData[field] = escape(request.form[field])

			for field in optionalFields:
				try:
					formData[field] = escape(request.form[field])
				except:
					formData[field] = None

			# The sheet stores data in this formmat:
			# Date, Time, State, District, Infected, Death, Source Link, Name
			submitList = [
				formData['date'],
				datetime.now().strftime("%H:%M"),
				formData['state'],
				formData['district']
			]
			if formData['infected'] in ["True", 'true', True]:
				submitList.append(formData['number'])
				submitList.append(None)
			else:
				submitList.append(None)
				submitList.append(formData['number'])
			submitList.append(formData['source'])
			submitList.append(formData['name'])

			scope = ['https://spreadsheets.google.com/feeds']
			creds = ServiceAccountCredentials.from_json_keyfile_name(DIR_DATA + '/res/crowdsourcing_creds.json',scope)
			client = gspread.authorize(creds)

			with open(DIR_DATA + "/res/crowdsourcing_URL", 'r') as F:
				URL = F.read()
			sheet = client.open_by_url(URL).worksheet('Sheet1')

			sheet.append_row(submitList)

			return jsonify({"success" : True, "message" : "Thank you!"})
		else:
			return jsonify({"success" : False, "message" : "Please post some data"})	
	except Exception as e:
		print (e)
		return jsonify({"success" : False, "message" : str(e)})

@app.route('/i-donated-a-rick-roll', methods=['GET'])
def donated():
	try:
		with open("rick_roll_count.json", 'r') as FPtr:
			rrJSON = load(FPtr)
		rrJSON["rick-rolled"] += 1
		with open("rick_roll_count.json", 'r') as FPtr:
			dump(rrJSON, FPtr)
	except:
		rrJSON = {"rick-rolled" : 1}
		with open("rick_roll_count.json", 'w') as FPtr:
			dump(rrJSON, FPtr)
	finally:
		print ("Rick rolled someone! :yay:")

	return jsonify({"message": "LMAO"})

#####################
# PUBLIC API IS ON A HOLD UNTIL IT CAN BE FIGURED OUT WHAT TO BE DONE
#####################

# @app.route('/covindia-history-district-data', methods=['GET'])
# def covindia_district_date_data():
# 	cdddJSON = {}
# 	with open(DIR_DATA + "/PublicData/covindia_district_date_data.json", 'r') as FPtr:
# 		cdddJSON = load(FPtr)
# 	return jsonify(cdddJSON)

# @app.route('/covindia-present-state-data', methods=['GET'])
# def covindia_state_data():
# 	csdJSON = {}
# 	with open(DIR_DATA + "/PublicData/covindia_state_data.json", 'r') as FPtr:
# 		csdJSON = load(FPtr)
# 	return jsonify(csdJSON)

# @app.route('/covindia-present-general-data', methods=['GET'])
# def covindia_general_data():
# 	cgdJSON = {}
# 	with open(DIR_DATA + "/PublicData/covindia_general_data.json", 'r') as FPtr:
# 		cgdJSON = load(FPtr)
# 	return jsonify(cgdJSON)

# @app.route('/covindia-raw-data', methods=['GET'])
# def covindia_raw_data():
# 	crdJSON = {}
# 	with open(DIR_DATA + "/PublicData/covindia_raw_data.json", 'r') as FPtr:
# 		crdJSON = load(FPtr)
# 	return jsonify(crdJSON)

# @app.route('/covindia-raw-data-csv', methods=['GET'])
# def covindia_raw_data_csv():
# 	return send_file(DIR_DATA + '/PublicData/covindia_raw_data_csv.csv', mimetype='text/csv', attachment_filename='covindia_raw_data.csv', as_attachment=True)

#####################
# PUBLIC API ENDS
#####################