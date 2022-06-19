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
	"1450", "1451", "1452", "1453", "1454", "1455", "1456", "1457", "1458", "1459",    
	"2950", "2951", "2952", "2953", "2954", "2955", "2956", "2957", "2958", "2959",   
	"4450", "4451", "4452", "4453", "4454", "4455", "4456", "4457", "4458", "4459",    
	"5950", "5951", "5952", "5953", "5954", "5955", "5956", "5957", "5958", "5959"
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

		
		elif scriptJson['side'] == "CLOSE":

			print("\n --- Order -> CLOSE --- ")

			if Operation['status'] == True:
				getUsers_cancel()

				getUsers_checkInter()

			else:
				print("Not Operation to Close\n")


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

	print("\n-------------------- Create -------------------- \n")

	def inTimeCreate():
		orderTime1 = time.localtime()
		orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

		if orderTime in clock:
			bots = mongo.db.Bots
			pairFormat = {"pair": "BTCUSDT"}
			thisPairBot = bots.find(pairFormat)

			databaseBots = []

			for bot in thisPairBot:
				if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
					databaseBots.append(bot)

			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(createOrders, databaseBots)

		else:
			time.sleep(1)
			inTimeCreate()


	inTimeCreate()

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
	if scriptJson['side'] == "BUY":	
		profitPrice = ( priceBUSD + ( priceBUSD * 0.0025 ) )
	elif scriptJson['side'] == "SELL":	
		profitPrice = ( priceBUSD - ( priceBUSD * 0.0025 ) )
	else:
		print("ERROR PROFIT PRICE")

	status.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": True, "side": scriptJson['side'], "entryPrice": priceBUSD, "profitPrice": profitPrice}})

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
	global issues, tradeAmount, dataLog, orderPrice
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
		
		def createMarketOrderBinance():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues, tradeAmount

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				ticker = binance.fetch_ticker('BTC/BUSD')
				orderPrice1 = float(ticker['close'])
				orderPrice = orderPrice1
				tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

				try:
					if Operation['side'] == "BUY":
						order = binance.create_market_buy_order('BTC/BUSD', tradeAmount)
						issues = "None"
					elif Operation['side'] == "SELL":
						order = binance.create_market_sell_order('BTC/BUSD', tradeAmount)
						issues = "None"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "Insufficients founds"
			
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
			
			global order, issues, tradeAmount

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:

				ticker = bybit.fetch_ticker('BTC/BUSD')
				orderPrice1 = float(ticker['close'])
				orderPrice = orderPrice1
				tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

				try:
					if Operation['side'] == "BUY":
						order = bybit.create_market_buy_order('BTC/BUSD', tradeAmount)
						issues = "None"
					elif Operation['side'] == "SELL":
						order = bybit.create_market_sell_order('BTC/BUSD', tradeAmount)
						issues = "None"
					else:
						print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
						issues = "Invalid data"
				except:
					issues = "Insufficients founds"

			else:
				time.sleep(1)
				createMarketOrderBybit()	


		createMarketOrderBybit()
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

	def inTimeCancel():
		orderTime1 = time.localtime()
		orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

		if orderTime in clock:
			bots = mongo.db.Bots
			pairFormat = {"pair": "BTCUSDT"}
			thisPairBot = bots.find(pairFormat)

			databaseBots = []

			for bot in thisPairBot:
				if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
					databaseBots.append(bot)

			with concurrent.futures.ThreadPoolExecutor() as executor:
				executor.map(cancelOrders, databaseBots)

		else:
			time.sleep(1)
			inTimeCancel()


	inTimeCancel()
	
	status = mongo.db.Status
	status.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "entryPrice": 0.00, "profitPrice": 0.00}})

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





# --- Revisa continuamente el estado de las ordenes en base a los parametros ---
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

			binance = ccxt.binance({
			'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
			'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
			'options': {'defaultType': 'future',},})
			binance.enableRateLimit = True
			tickerBUSD = binance.fetch_ticker('BTC/BUSD')
			priceBUSD = float(tickerBUSD['close'])


			if Operation['side'] == "BUY":
				if priceBUSD > Operation['profitPrice']:

					databaseBots = []

					for bot in thisPairBot:
						if bot['isEnabled'] == True and bot['isEnabledforTrade'] == True:
							databaseBots.append(bot)

					with concurrent.futures.ThreadPoolExecutor() as executor:
						executor.map(checkOrders, databaseBots)

			elif Operation['side'] == "SELL":
				if priceBUSD < Operation['profitPrice']:

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

			try:
				if Operation['side'] == "BUY":
					binance.create_market_sell_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
					issues = "Limit Profit Reached"
				elif Operation['side'] == "SELL":
					binance.create_market_buy_order('BTC/BUSD', thisBot['lastOrderAmount'], params={'reduce_only': True})
					issues = "Limit Profit Reached"
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
		

		checkMarketOrderBinance()
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		def checkMarketOrderBybit():

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


		checkMarketOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"





# --- Revisa entre operaciones el estado de las cuentas en base a los parametros ---
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
			executor.map(updateBots, databaseBots)

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

time10 = datetime.timedelta(seconds=3)
scheduleBTC.cyclic(time10, getUsers_check, args=(mty,))

# -------------------- Schedule --------------------