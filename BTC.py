from flask import Blueprint, render_template, request, current_app as app
from Mongo.extensions import mongo
from scheduler import Scheduler
import concurrent.futures
import datetime
import time
import ccxt
import pytz

# --------------

BTC = Blueprint('BTC', __name__)

# --------------

lockThisFunction = False
clock = [
	"415", "416", "417", "418", "419", "420", "421", "422", "423", "424", "425", "426", "427", "428", "429", "430", "431", "432", "433", "434", "435", "436", "437", "438", "439", "440", "441", "442", "0443", "0444", "0445", "446", "447", "448", "449", "450", "451", "452", "453", "454", "455", "456", "457", "458", "459",
	"915", "916", "917", "918", "919", "920", "921", "922", "923", "924", "925", "926", "927", "928", "929", "930", "931", "932", "933", "934", "935", "936", "937", "938", "939", "940", "941", "942", "0943", "0944", "0945", "946", "947", "948", "949", "950", "951", "952", "953", "954", "955", "956", "957", "958", "959",
	"1415", "1416", "1417", "1418", "1419", "1420", "1421", "1422", "1423", "1424", "1425", "1426", "1427", "1428", "1429", "1430", "1431", "1432", "1433", "1434", "1435", "1436", "1437", "1438", "1439", "1440", "1441", "1442", "1443", "1444", "1445", "1446", "1447", "1448", "1449", "1450", "1451", "1452", "1453", "1454", "1455", "1456", "1457", "1458", "1459",  
	"1915", "1916", "1917", "1918", "1919", "1920", "1921", "1922", "1923", "1924", "1925", "1926", "1927", "1928", "1929", "1930", "1931", "1932", "1933", "1934", "1935", "1936", "1937", "1938", "1939", "1940", "1941", "1942", "1943", "1944", "1945", "1946", "1947", "1948", "1949", "1950", "1951", "1952", "1953", "1954", "1955", "1956", "1957", "1958", "1959",  
	"2415", "2416", "2417", "2418", "2419", "2420", "2421", "2422", "2423", "2424", "2425", "2426", "2427", "2428", "2429", "2430", "2431", "2432", "2433", "2434", "2435", "2436", "2437", "2438", "2439", "2440", "2441", "2442", "2443", "2444", "2445", "2446", "2447", "2448", "2449", "2450", "2451", "2452", "2453", "2454", "2455", "2456", "2457", "2458", "2459",  
	"2915", "2916", "2917", "2918", "2919", "2920", "2921", "2922", "2923", "2924", "2925", "2926", "2927", "2928", "2929", "2930", "2931", "2932", "2933", "2934", "2935", "2936", "2937", "2938", "2939", "2940", "2941", "2942", "2943", "2944", "2945", "2946", "2947", "2948", "2949", "2950", "2951", "2952", "2953", "2954", "2955", "2956", "2957", "2958", "2959",  
	"3415", "3416", "3417", "3418", "3419", "3420", "3421", "3422", "3423", "3424", "3425", "3426", "3427", "3428", "3429", "3430", "3431", "3432", "3433", "3434", "3435", "3436", "3437", "3438", "3439", "3440", "3441", "3442", "3443", "3444", "3445", "3446", "3447", "3448", "3449", "3450", "3451", "3452", "3453", "3454", "3455", "3456", "3457", "3458", "3459",  
	"3915", "3916", "3917", "3918", "3919", "3920", "3921", "3922", "3923", "3924", "3925", "3926", "3927", "3928", "3929", "3930", "3931", "3932", "3933", "3934", "3935", "3936", "3937", "3938", "3939", "3940", "3941", "3942", "3943", "3944", "3945", "3946", "3947", "3948", "3949", "3950", "3951", "3952", "3953", "3954", "3955", "3956", "3957", "3958", "3959",  
	"4415", "4416", "4417", "4418", "4419", "4420", "4421", "4422", "4423", "4424", "4425", "4426", "4427", "4428", "4429", "4430", "4431", "4432", "4433", "4434", "4435", "4436", "4437", "4438", "4439", "4440", "4441", "4442", "4443", "4444", "4445", "4446", "4447", "4448", "4449", "4450", "4451", "4452", "4453", "4454", "4455", "4456", "4457", "4458", "4459",  
	"4915", "4916", "4917", "4918", "4919", "4920", "4921", "4922", "4923", "4924", "4925", "4926", "4927", "4928", "4929", "4930", "4931", "4932", "4933", "4934", "4935", "4936", "4937", "4938", "4939", "4940", "4941", "4942", "4943", "4944", "4945", "4946", "4947", "4948", "4949", "4950", "4951", "4952", "4953", "4954", "4955", "4956", "4957", "4958", "4959",  
	"5415", "5416", "5417", "5418", "5419", "5420", "5421", "5422", "5423", "5424", "5425", "5426", "5427", "5428", "5429", "5430", "5431", "5432", "5433", "5434", "5435", "5436", "5437", "5438", "5439", "5440", "5441", "5442", "5443", "5444", "5445", "5446", "5447", "5448", "5449", "5450", "5451", "5452", "5453", "5454", "5455", "5456", "5457", "5458", "5459",  
	"5915", "5916", "5917", "5918", "5919", "5920", "5921", "5922", "5923", "5924", "5925", "5926", "5927", "5928", "5929", "5930", "5931", "5932", "5933", "5934", "5935", "5936", "5937", "5938", "5939", "5940", "5941", "5942", "5943", "5944", "5945", "5946", "5947", "5948", "5949", "5950", "5951", "5952", "5953", "5954", "5955", "5956", "5957", "5958", "5959"  
]


# --- Pagina Visual HTML, inicio de ciclo para schedule
@BTC.route('/BTC', methods=['GET'])
def btc():
	binance = ccxt.binance({
		'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
		'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
		'options': {'defaultType': 'future',},})
	binance.enableRateLimit = True
	ticker = binance.fetch_ticker('BTC/BUSD')
	price = float(ticker['close'])
	
	status = mongo.db.Status
	operationFilter = {"Operation-BTC": True}
	Operation = status.find_one(operationFilter)

	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
	date = dateTime.strftime("%d/%m/%y")
	logFilter = {"Log-BTC": True}
	Log = status.find_one(logFilter)
	Logs = Log['Log']
	

	if Operation['status'] == True: OperationColor = "primary"
	else: OperationColor = "secondary"
	if Operation['side'] == "BUY": SideColor = "success"
	elif Operation['side'] == "SELL": SideColor = "danger"
	else: SideColor = "secondary"
	if Operation['entryPrice'] == 0: epColor = "secondary"
	else: epColor = "primary"
	if Operation['status'] == True and Operation['side'] == "BUY" and price > Operation['entryPrice']: priceColor = "success"
	elif Operation['status'] == True and Operation['side'] == "BUY" and price < Operation['entryPrice']: priceColor = "danger"
	elif Operation['status'] == True and Operation['side'] == "SELL" and price < Operation['entryPrice']: priceColor = "success"
	elif Operation['status'] == True and Operation['side'] == "SELL" and price > Operation['entryPrice']: priceColor = "danger"
	else: priceColor = "secondary"
	if Operation['todayProfit'] > 0: profitColor = "success"
	else: profitColor = "danger"


	return render_template('Currencies/bitcoin.html',
	Operation=Operation['status'],
	OperationColor=OperationColor,
	Side=Operation['side'],
	SideColor=SideColor,
	EntryP=Operation['entryPrice'],
	epColor=epColor,
	Price=price,
	PriceColor=priceColor,
	Profit=Operation['todayProfit'],
	ProfitColor=profitColor,
	Logs=Logs)

# --- Sin uso por el momento, anteriormente servia como limite de perdida y limite de ganancia ---
@BTC.route('/Price-BTC', methods=['POST'])
def Price():
	@app.after_response
	def afterPrice():
		pass
		# --- Proximamente OLHC chart---
		pass

	return 'Ciclo Reiniciado'

# --- Define la direccion y los parametros de las operaciones ---
@BTC.route('/Script-BTC', methods=['POST'])
def script():
	global scriptJson
	scriptJson = request.json
	@app.after_response
	def afterSar():
		status = mongo.db.Status
		operationFilter = {"Operation-BTC": True}	
		Operation = status.find_one(operationFilter)
		server = "SERVER"

		if scriptJson['side'] == "BUY":
			
			print("\n --- Order -> BUY --- ")

			if Operation['status'] == True:
				if Operation['side'] == "BUY":
					print(" --- Operation is Already BUY --- \n")
				else:
					getUsers_cancel()

					getUsers_checkInter()

					if Operation['updatePending'] == True:
						print(" --- Update Pending --- \n")
						getUsers_update(server)

					getUsers_create()
			else:
				getUsers_checkInter()

				if Operation['updatePending'] == True:
					print("Update Pending\n")
					getUsers_update(server)

				getUsers_create()


		elif scriptJson['side'] == "SELL":

			print("\n --- Order -> SELL --- ")

			if Operation['status'] == True:
				if Operation['side'] == "SELL":
					print("Operation is Already SELL\n")
				else:
					getUsers_cancel()

					getUsers_checkInter()

					if Operation['updatePending'] == True:
						getUsers_update(server)

					getUsers_create()
			else:
				getUsers_checkInter()

				if Operation['updatePending'] == True:
					getUsers_update(server)

				getUsers_create()	

		
		elif scriptJson['side'] == "CANCEL":

			print("\n --- Order -> CANCEL --- ")

			if Operation['status'] == True:
				getUsers_cancel()

				getUsers_checkInter()

			else:
				print("Not Operation to Cancel\n")


		else:
			print("Error Request")

	return 'Operacion Realizada'





# --- Crea Operaciones en base a los parametros ---
def getUsers_create():
	global lockThisFunction
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_create()
	lockThisFunction = True

	status = mongo.db.Status
	operationFilter = {"Operation-BTC": True}	
	Operation = status.find_one(operationFilter)

	status.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": True, "side": scriptJson['side'], "entryPrice": scriptJson['close']}})

	print("\n-------------------- Create -------------------- \n")

	bots = mongo.db.Bots
	pairFormat = {"pair": "BTCUSDT"}
	thisPairBot = bots.find(pairFormat)

	databaseBots = []

	for bot in thisPairBot:
		if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
			databaseBots.append(bot)

	with concurrent.futures.ThreadPoolExecutor() as executor:
		executor.map(createOrders, databaseBots)

	print("\n-------------------- Create -------------------- \n")

	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")

	binance = ccxt.binance({
		'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
		'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
		'options': {'defaultType': 'future',},})
	binance.enableRateLimit = True
	tickerBUSD = binance.fetch_ticker('BTC/BUSD')
	priceBUSD = float(tickerBUSD['close'])

	newLog = {
		"status": "Open",
		"side": scriptJson['side'],

		"dateOpen": date,
		"timeOpen": ctime,
		"priceOpen": priceBUSD,

		"dateClose": "-",
		"timeClose": "-",
		"priceClose": 0.00,

		"singleProfit": 0.00,
		"acumulateProfit": 0.00
	}

	status.update(
		{"Log-BTC": True},
		{"$push":
			{
				"Log": newLog
			} 
		}
	)

	lockThisFunction = False
	
def createOrders(thisBot):
	global issues, tradeAmount, dataLog
	issues = "None"
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)
	

	#-------------------- BINANCE -------------------- 
	if thisBot['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		binance.set_leverage(thisBot['quantityLeverage'], 'BTC/BUSD', params={"marginMode": "isolated"})

		def createLimitOrderBinance():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues, tradeAmount, orderPrice
			retrying = False
			thisOrder = False

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				ticker = binance.fetch_ticker('BTC/BUSD')
				orderPrice1 = float(ticker['close'])
				orderPrice = orderPrice1
				tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

				try:
					if Operation['side'] == "BUY":
						order = binance.create_limit_buy_order('BTC/BUSD', tradeAmount, orderPrice)
						thisOrder = True
					elif Operation['side'] == "SELL":
						order = binance.create_limit_sell_order('BTC/BUSD', tradeAmount, orderPrice)
						thisOrder = True
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
				except:
					if retrying == True:
						issues = "None"
						retrying = False
						thisOrder = False
					else:
						issues = "Insufficients founds"
						thisOrder = False
			
			else:
				time.sleep(1)
				createLimitOrderBinance()
			
			
			time.sleep(3)
			if (thisOrder == True) and (order['status'] == "open"):
				retrying = True
				thisOrder = False
				binance.cancel_all_orders('BTC/BUSD')
				createLimitOrderBinance()


		createLimitOrderBinance()
		
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		bybit.set_leverage(thisBot['quantityLeverage'], 'BTC/BUSD', params={"marginMode": "isolated"})

		def createLimitOrderBybit():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues, tradeAmount, orderPrice
			retrying = False
			thisOrder = False

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				ticker = bybit.fetch_ticker('BTC/BUSD')
				orderPrice1 = float(ticker['close'])
				orderPrice = orderPrice1
				tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

				try:
					if Operation['side'] == "BUY":
						order = bybit.create_limit_buy_order('BTC/BUSD', tradeAmount, orderPrice)
						thisOrder = True
					elif Operation['side'] == "SELL":
						order = bybit.create_limit_sell_order('BTC/BUSD', tradeAmount, orderPrice)
						thisOrder = True
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
				except:
					if retrying == True:
						issues = "None"
						retrying = False
						thisOrder = False
					else:
						issues = "Insufficients founds"
						thisOrder = False

			else:
				time.sleep(1)
				createLimitOrderBybit()
			
			
			time.sleep(3)
			if (thisOrder == True) and (order['status'] == "open"):
				retrying = True
				thisOrder = False
				bybit.cancel_all_orders('BTC/BUSD')
				createLimitOrderBybit()


		createLimitOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Invalid Exchange"
		
	bots = mongo.db.Bots	
	bots.update_one(
		{"_id": thisBot['_id']},
		{"$set": {"lastOrderAmount": tradeAmount}})

	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")

	bots.update(
		{"_id": thisBot['_id']},
		{"$push": 
			{"log":
		{
			"status": "Open",
			"side": Operation['side'],
			"amount": tradeAmount,
			"dateOpen": date,
			"timeOpen": ctime,
			"priceOpen": order['price'],
			"issuesOpen": issues,
			"dateClose": "-",
			"timeClose": "-",
			"priceClose": 0.00,
			"issuesClose": "-",
			"profit": 0.00
		}}})

	print(" Bot: " + str(thisBot['exchangeConnection']['apiKey']) + "key created at $" + str(orderPrice)+ " with '" + str(issues) + "' isues")





# --- Cancela Operaciones en base a los parametros ---
def getUsers_cancel():
	global lockThisFunction
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_cancel()
	lockThisFunction = True

	print("\n-------------------- CANCEL -------------------- \n")

	bots = mongo.db.Bots
	pairFormat = {"pair": "BTCUSDT",}
	thisPairBot = bots.find(pairFormat)

	databaseBots = []

	for bot in thisPairBot:
		if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
			databaseBots.append(bot)

	with concurrent.futures.ThreadPoolExecutor() as executor:
		executor.map(cancelOrders, databaseBots)
	
	status = mongo.db.Status
	status.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "entryPrice": 0.00}})

	print("\n-------------------- CANCEL -------------------- \n")

	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")

	binance = ccxt.binance({
		'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
		'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
		'options': {'defaultType': 'future',},})
	binance.enableRateLimit = True
	tickerBUSD = binance.fetch_ticker('BTC/BUSD')
	priceBUSD = float(tickerBUSD['close'])
	
	logFilter = {"Log-BTC": True}	
	log = status.find_one(logFilter)

	thisOrder = log['Log'][-1]
	lastOrder = log['Log'][-2]
	
	if thisOrder['side'] == "BUY":
		singleProfit = ( priceBUSD * 100 / (thisOrder['priceOpen']) ) - 100
	else:
		singleProfit = ( (thisOrder['priceOpen']) * 100 / priceBUSD ) - 100

	operationFilter = {"Operation-BTC": True}	
	Operation = status.find_one(operationFilter)

	if Operation['init'] == True:
		acumulateProfit = singleProfit
		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"init": False}})
	else:
		acumulateProfit = lastOrder['acumulateProfit'] + singleProfit

	status.update_one(
		{"Log-BTC": True, "Log.status": "Open"},
		{"$set": {
			"Log.$.status": "Close",
			"Log.$.dateClose": date,
			"Log.$.timeClose": ctime,
			"Log.$.priceClose": priceBUSD,
			"Log.$.singleProfit": singleProfit,
			"Log.$.acumulateProfit": acumulateProfit
			}
		}
	)

	lockThisFunction = False

def cancelOrders(thisBot):
	global issues, dataLog
	issues = "None"
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)
	
	#-------------------- BINANCE -------------------- 
	if thisBot['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		
		def createMarketOrderBinance():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				try:
					if Operation['side'] == "BUY":
						order = binance.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "None"
					elif Operation['side'] == "SELL":
						order = binance.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "None"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No order Open"
			
			else:
				time.sleep(1)
				createMarketOrderBinance()		

			

		createMarketOrderBinance()
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		def createMarketOrderBybit():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				try:
					if Operation['side'] == "BUY":
						order = bybit.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "None"
					elif Operation['side'] == "SELL":
						order = bybit.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "None"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No order Open"

			else:
				time.sleep(1)
				createMarketOrderBybit()	


		createMarketOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"

	dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
	dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")

	if Operation['side'] == "BUY":
		profit = ( order['price'] * 100 / (thisBot['log'][-1]['priceOpen']) ) - 100
	else:
		profit = ( (thisBot['log'][-1]['priceOpen']) * 100 / order['price'] ) - 100

	bots = mongo.db.Bots
	bots.update_one(
		{"_id": (thisBot['_id']), "log.status": "Open"},
		{"$set": {
			"log.$.status": "Close", 
			"log.$.dateClose": date, 
			"log.$.timeClose": ctime,
			"log.$.priceClose": order['price'],
			"log.$.issuesClose": issues,
			"log.$.profit": profit}})

	print(" Bot: " + str(thisBot['exchangeConnection']['apiKey']) + "key canceled with '" + str(issues) + "' isues")

	dataLog = {
		"dateOpen": date,
		"timeOpen": ctime,
		"priceOpen": order['price']
	}





# --- Revisa continuamente el estado de las cuentas en base a los parametros ---
def getUsers_check(server1):
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		pass
	else:
		pairFormat = {"pair": "BTCUSDT"}
		bots = mongo.db.Bots
		thisPairBot = bots.find(pairFormat)

		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)

		if Operation['status'] == True:
			databaseBots = []

			for bot in thisPairBot:
				if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
					databaseBots.append(bot)

			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(checkOrders, databaseBots)
		else:
			print(" Not in Operation -- BTC -- ")

def checkOrders(thisBot):
	global issues
	issues = ""
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)
	
	#-------------------- BINANCE -------------------- 
	if thisBot['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		
		def checkMarketOrderBinance():
			
			balance = binance.fetch_balance()
			balanceBUSD = balance['BUSD']['total']

			if balanceBUSD < thisBot['limitAmount']:
				global issues
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Limit Balance Reached -- ")

				try:
					if Operation['side'] == "BUY":
						binance.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					elif Operation['side'] == "SELL":
						binance.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No Order Open"

				bots = mongo.db.Bots
				dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
				dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
				date = dateTime.strftime("%d/%m/%y")
				ctime = dateTime.strftime("%H:%M:%S")
				bots.update_one(
					{"_id": (thisBot['_id']), "log.status": "Open"},
					{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": ctime, "log.$.issuesClose": issues}})
				
				bots.update_one(
					{"_id": (thisBot['_id'])},
					{"$set": {"isEnabledforTrade": False}})
			else:
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Balance in Range --  ")


		checkMarketOrderBinance()
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		def checkMarketOrderBybit():
			
			balance = bybit.fetch_balance()
			balanceBUSD = balance['BUSD']['total']

			if balanceBUSD < thisBot['limitAmount']:
				global issues
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Limit Balance Reached -- ")

				try:
					if Operation['side'] == "BUY":
						bybit.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					elif Operation['side'] == "SELL":
						bybit.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No Order Open"

				bots = mongo.db.Bots
				dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
				dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
				date = dateTime.strftime("%d/%m/%y")
				ctime = dateTime.strftime("%H:%M:%S")
				bots.update_one(
					{"_id": (thisBot['_id']), "log.status": "Open"},
					{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": ctime, "log.$.issuesClose": issues}})
				
				bots.update_one(
					{"_id": (thisBot['_id'])},
					{"$set": {"isEnabledforTrade": False}})

			else:
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Balance in Range --  ")


		checkMarketOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"





# --- Revisa continuamente el estado de las cuentas en base a los parametros ---
def getUsers_checkInter():
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		pass
	else:
		pairFormat = {"pair": "BTCUSDT"}
		bots = mongo.db.Bots
		thisPairBot = bots.find(pairFormat)
		
		databaseBots = []

		for bot in thisPairBot:
			if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
				databaseBots.append(bot)

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.map(checkOrdersInter, databaseBots)
		

def checkOrdersInter(thisBot):
	global issues
	issues = ""
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)
	
	#-------------------- BINANCE -------------------- 
	if thisBot['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		
		def checkMarketOrderBinance():
			
			balance = binance.fetch_balance()
			balanceBUSD = balance['BUSD']['total']

			if balanceBUSD < thisBot['tradeAmount']:
				global issues
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Limit Balance Reached -- ")

				try:
					if Operation['side'] == "BUY":
						binance.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					elif Operation['side'] == "SELL":
						binance.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No Order Open"

				bots = mongo.db.Bots
				dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
				dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
				date = dateTime.strftime("%d/%m/%y")
				ctime = dateTime.strftime("%H:%M:%S")
				bots.update_one(
					{"_id": (thisBot['_id']), "log.status": "Open"},
					{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": ctime, "log.$.issuesClose": issues}})
				
				bots.update_one(
					{"_id": (thisBot['_id'])},
					{"$set": {"isEnabledforTrade": False}})
			else:
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Balance in Range --  ")


		checkMarketOrderBinance()
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		def checkMarketOrderBybit():
			
			balance = bybit.fetch_balance()
			balanceBUSD = balance['BUSD']['total']

			if balanceBUSD < thisBot['tradeAmount']:
				global issues
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Limit Balance Reached -- ")

				try:
					if Operation['side'] == "BUY":
						bybit.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					elif Operation['side'] == "SELL":
						bybit.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
						issues = "Limit Balance Reached"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "No Order Open"

				bots = mongo.db.Bots
				dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
				dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
				date = dateTime.strftime("%d/%m/%y")
				ctime = dateTime.strftime("%H:%M:%S")
				bots.update_one(
					{"_id": (thisBot['_id']), "log.status": "Open"},
					{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": ctime, "log.$.issuesClose": issues}})
				
				bots.update_one(
					{"_id": (thisBot['_id'])},
					{"$set": {"isEnabledforTrade": False}})

			else:
				print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " -- Balance in Range --  ")


		checkMarketOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"





# --- Actualiza cada 24hrs la base de datos de usuarios en base a los parametros ---
def getUsers_update(server3):
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_update()
	lockThisFunction = True

	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)

	if Operation['status'] == True:
		
		print("\n-------------------- UPDATE IN OPERATION -------------------- \n")

		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"updatePending": True}})

	else:
		print("\n-------------------- UPDATE -------------------- \n")

		bots = mongo.db.Bots
		pairFormat = {"pair": "BTCUSDT",}
		thisPairBot = bots.find(pairFormat)

		databaseBots = []

		for bot in thisPairBot:
			if bot['isEnabled'] == True:
				databaseBots.append(bot)

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.map(checkOrders, databaseBots)

		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"updatePending": False, "init": True}})

	print("\n-------------------- UPDATE -------------------- \n")
	
	lockThisFunction = False

def updateBots(thisBot):
	#-------------------- BINANCE -------------------- 
	if thisBot['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		
		balance = binance.fetch_balance()
		balanceBUSD = balance['BUSD']['total']
		newTradeAmount = balanceBUSD * .75
		newLimitAmount = balanceBUSD * .68

		bots = mongo.db.Bots	
		bots.update_one(
			{"_id": thisBot['_id']},
			{"$set": {"tradeAmount": round(newTradeAmount, 2), "limitAmount": round(newLimitAmount, 2), "isEnabledforTrade": True}})

	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		balance = bybit.fetch_balance()
		balanceBUSD = balance['BUSD']['total']
		newTradeAmount = balanceBUSD * .75

		bots = mongo.db.Bots	
		bots.update_one(
			{"_id": thisBot['_id']},
			{"$set": {"tradeAmount": round(newTradeAmount, 2), "isEnabledforTrade": True}})

	print("\n Bot: " + str(thisBot['exchangeConnection']['apiKey']) + " tradeAmount updated to " + str(round(newTradeAmount, 2)))





# -------------------- Schedule --------------------

server = datetime.timezone.utc
mty = pytz.timezone('America/Monterrey')
scheduleBTC = Scheduler(tzinfo=server)

time00 = datetime.time(hour=0, tzinfo=mty)
scheduleBTC.daily(time00, getUsers_update, args=(mty,))

time10 = datetime.timedelta(seconds=10)
scheduleBTC.cyclic(time10, getUsers_check, args=(mty,))

# -------------------- Schedule --------------------