from flask import Blueprint, request, render_template
from Mongo.extensions import mongo
from bson.objectid import ObjectId


appTest = Blueprint('appTest', __name__)


@appTest.route('/addUser', methods=['POST'])
def addUser():

	user = mongo.db.Users
	user.insert_one(request.json)

	return 'User added'

@appTest.route('/addBot', methods=['POST'])
def addBot():

	bot = mongo.db.Bots
	bot.insert_one(request.json)

	return 'Bot added'

@appTest.route('/addStatus', methods=['POST'])
def addStatus():

	status = mongo.db.Status
	status.insert_one(request.json)

	return 'Status added'

@appTest.route('/updateOp', methods=['POST'])
def updateOP():

	operation = mongo.db.Status
	
	if request.json['Operation-BTC'] == True:
		id = "622cf1cf640ef23c1cdce00b"
		operation.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- Operation -> " + str(status) + " --- \n")
	else:
		print("Error en Operation")

	return 'Operation Actualizado'

# -----------------------------------------------------------------------    
	
@appTest.route('/', methods=['GET'])
def index_en():
	return render_template('EN/index_en.html')

@appTest.route('/es', methods=['GET'])
def index_es():
	return render_template('ES/index_es.html')

@appTest.route('/request', methods=['GET', 'POST'])
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

@appTest.route('/request-es', methods=['GET', 'POST'])
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

import ccxt
import datetime

@appTest.route('/test', methods=['GET', 'POST'])
def test():
	bybit = ccxt.bybit({
			'apiKey': 'd7QTP08KaYjLtdooCJ',
			'secret': 'G2Kpfs3tR7DODcm5isMdUpka8adcrwbZ8M5S',
			'options': {
				'defaultType': 'future',
			},
		})
	balance = bybit.fetch_balance()
	balanceUSDT = balance['USDT']['total']
	datetime_object = datetime.datetime.now()
	return str(balanceUSDT) + '    ' + str(datetime_object)