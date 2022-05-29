from itertools import accumulate
from pickle import OBJ
from re import X
from flask import Blueprint, jsonify, render_template, request, current_app as app
from Mongo.extensions import mongo
from bson.objectid import ObjectId
from scheduler import Scheduler
import time
import ccxt
import datetime
import pytz

from BTC import scheduleBTC
from ETH import scheduleETH

# RECORDATORIO DE ORDENAR T0D0 ESTE JALE


appRoutes = Blueprint('appRoutes', __name__)


# -----------------------------------------------------------------------
#								FRONTEND
# -----------------------------------------------------------------------

@appRoutes.route('/', methods=['GET'])
def index_en():
	return render_template('index.html')

@appRoutes.route('/Login', methods=['GET'])
def login():
	return render_template('login.html')

@appRoutes.route('/Register', methods=['GET'])
def register():
	return render_template('register.html')

@appRoutes.route('/Dashboard', methods=['GET'])
def dashboard():
	return render_template('Dashboard/dashboard.html')

@appRoutes.route('/Notifications', methods=['GET'])
def notifications():
	return render_template('Dashboard/notifications.html')

@appRoutes.route('/Bots', methods=['GET'])
def bots():
	return render_template('Dashboard/bots.html') # --- 404 ---

@appRoutes.route('/Help', methods=['GET'])
def help():
	return render_template('Dashboard/help.html')



# -----------------------------------------------------------------------
#								BACKTEND
# -----------------------------------------------------------------------

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

	#order = binance.create_market_sell_order('BTC/BUSD', 0.001)
	#print(str(order['price']) + '\n\n')

	time.sleep(1)

	#order1 = binance.create_market_buy_order('BTC/BUSD', 0.001, params={'reduce_only': True})
	#print(str(order1['price']) + '\n\n')

	profit = 29228 * 100 / 29123.2   # BUY  primero entrada y luego salida
	profit = 29172.5 * 100 / 29123.2 # SELL primero salida luego entrada
	singleProfit = profit - 100
	print(str(round(singleProfit, 3)))

	return str(balanceUSDT) + '    ' + str(datetime_object)

@appRoutes.route('/log', methods=['POST'])
def log():

	status = mongo.db.Status
	logFilter = {"Log-BTC": True}	
	log = status.find_one(logFilter)

	thisOrder = log['Log'][-1]
	lastOrder = log['Log'][-2]
	
	if thisOrder['side'] == "BUY":
		singleProfit = ( 31000 * 100 / (thisOrder['priceOpen']) ) - 100
	else:
		singleProfit = ( (thisOrder['priceOpen']) * 100 / 29000 ) - 100

	acumulateProfit = lastOrder['acumulateProfit'] + singleProfit

	print(singleProfit)
	print(acumulateProfit)
	

	return 'log'

@appRoutes.route('/Schedule', methods=['POST'])
def scheduler():
	print(scheduleBTC)
	#print(scheduleETH)
	@app.after_response
	def init():
		while True:
			scheduleBTC.exec_jobs()
			#scheduleETH.exec_jobs()
			time.sleep(10)
	return 'Scheduel'

@appRoutes.route('/testbot', methods=['POST'])
def testbot():
	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))

	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")

	print(date)
	print(ctime)
	return 'did'