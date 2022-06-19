from flask import Blueprint, jsonify, render_template, request, current_app as app
from Mongo.extensions import mongo
from bson.objectid import ObjectId
from scheduler import Scheduler
import time
import ccxt
import datetime
import pytz

from BTC import scheduleBTC
#from ETH import scheduleETH

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

@appRoutes.route('/Schedule', methods=['POST'])
def scheduler():
	print(scheduleBTC)
	#print(scheduleETH)
	@app.after_response
	def init():
		while True:
			scheduleBTC.exec_jobs()
			#scheduleETH.exec_jobs()
			time.sleep(3)
	return 'Scheduel'

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
	@app.after_response
	def cre():
		import time
		binance = ccxt.binance({
				'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
				'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
				'options': {
					'defaultType': 'future',
				},
			})
		binance.set_leverage(50, 'BTC/BUSD', params={"marginMode": "isolated"})
		#datetime_object = datetime.datetime.now()
		#tickerBUSD = binance.fetch_ticker('BTC/BUSD')
		#priceBUSD = float(tickerBUSD['close'])
		tradeAmount = 0.001
		clock = [
		"450", "451", "452", "453", "454", "455", "456", "457", "458", "459",
		"950", "951", "952", "953", "954", "955", "956", "957", "958", "959",
		"1450", "1451", "1452", "1453", "1454", "1455", "1456", "1457", "1458", "1459",  
		"1950", "1951", "1952", "1953", "1954", "1955", "1956", "1957", "1958", "1959",  
		"2450", "2451", "2452", "2453", "2454", "2455", "2456", "2457", "2458", "2459",  
		"2950", "2951", "2952", "2953", "2954", "2955", "2956", "2957", "2958", "2959",  
		"3450", "3451", "3452", "3453", "3454", "3455", "3456", "3457", "3458", "3459",  
		"3950", "3951", "3952", "3953", "3954", "3955", "3956", "3957", "3958", "3959",  
		"4450", "4451", "4452", "4453", "4454", "4455", "4456", "4457", "4458", "4459",  
		"4950", "4951", "4952", "4953", "4954", "4955", "4956", "4957", "4958", "4959",  
		"5450", "5451", "5452", "5453", "5454", "5455", "5456", "5457", "5458", "5459",  
		"5950", "5951", "5952", "5953", "5954", "5955", "5956", "5957", "5958", "5959"  
		]
		
		def create():
			import time
			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:
				order = binance.create_market_sell_order('BTC/BUSD', tradeAmount)
				print(order['datetime'])
				print(order['price'])

				time.sleep(3)

				order = binance.create_market_buy_order('BTC/BUSD', tradeAmount, params={'reduce_only': True})	
				print(order['datetime'])
				print(order['price'])
			else:
				time.sleep(1.1)
				create()

		create()

	return 'did'

