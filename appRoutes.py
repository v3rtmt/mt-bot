from flask import Blueprint, render_template, request, current_app as app
from Mongo.extensions import mongo
import time
import schedule



appRoutes = Blueprint('appRoutes', __name__)


@appRoutes.route('/addUser', methods=['POST'])
def addUser():

	user = mongo.db.Users
	user.insert_one(request.json)

	return 'User added'

@appRoutes.route('/addBot', methods=['POST'])
def addBot():

	bot = mongo.db.Bots
	bot.insert_one(request.json)

	return 'Bot added'

@appRoutes.route('/addStatus', methods=['POST'])
def addStatus():

	status = mongo.db.Status
	status.insert_one(request.json)

	return 'Status added'

# -----------------------------------------------------------------------    
	
@appRoutes.route('/', methods=['GET'])
def index_en():
	@app.after_response
	def init():
		while True:
			schedule.run_pending()
			time.sleep(6)

	return render_template('EN/index_en.html')

@appRoutes.route('/es', methods=['GET'])
def index_es():
	return render_template('ES/index_es.html')

@appRoutes.route('/request', methods=['GET', 'POST'])
def request_en():

	if request.form.get("name") == None:
		pass
	else:
		name = request.form.get("name")
		lastName = request.form.get("lastName")
		email = request.form.get("email")
		type = request.form.get("type")
		description = request.form.get("description")

		newRequest = {
			"Name": name,
			"Last Name": lastName,
			"Email": email,
			"Type": type,
			"Description": description 
		}

		setRequest = mongo.db.Request
		setRequest.insert_one(newRequest)

	return render_template('EN/requests.html')

@appRoutes.route('/request-es', methods=['GET', 'POST'])
def request_es():

	if request.form.get("name") == None:
		pass
	else:
		name = request.form.get("name")
		lastName = request.form.get("lastName")
		email = request.form.get("email")
		type = request.form.get("type")
		description = request.form.get("description")

		newRequest = {
			"Name": name,
			"Last Name": lastName,
			"Email": email,
			"Type": type,
			"Description": description 
		}

		setRequest = mongo.db.Request
		setRequest.insert_one(newRequest)

	return render_template('ES/requests.html')

@appRoutes.route('/unavailable', methods=['GET'])
def question():
	return render_template('question.html')

import ccxt
import datetime

@appRoutes.route('/test', methods=['GET', 'POST'])
def test():
	binance = ccxt.binance({
			'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
			'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
			'options': {
				'defaultType': 'future',
			},
		})
	balance = binance.fetch_balance()
	balanceUSDT = balance['BUSD']['total']
	datetime_object = datetime.datetime.now()
	return str(balanceUSDT) + '    ' + str(datetime_object)