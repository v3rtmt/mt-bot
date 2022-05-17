from flask import Blueprint, render_template, request, current_app as app
from Mongo.extensions import mongo
from datetime import datetime
import schedule
import requests
import time
import ccxt

# --------------

BTC = Blueprint('BTC', __name__)

# --------------

lockThisFunction = False


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

	if Operation['status'] == True: OperationColor = "primary"
	else: OperationColor = "secondary"
	if Operation['side'] == "BUY": SideColor = "success"
	elif Operation['side'] == "SELL": SideColor = "danger"
	else: SideColor = "secondary"
	if Operation['entryPrice'] == 0: epColor = "secondary"
	else: epColor = "primary"

	return render_template('bitcoin.html',
	Price=price,
	Operation=Operation['status'],
	OperationColor=OperationColor,
	Side=Operation['side'],
	SideColor=SideColor,
	EntryP=Operation['entryPrice'],
	epColor=epColor)

# --- Sin uso por el momento, anteriormente servia como limite de perdida y limite de ganancia ---
@BTC.route('/Price-BTC', methods=['POST'])
def Price():
	@app.after_response
	def afterPrice():
		#req = requests.post("https://mt-strategy.herokuapp.com/")
		req = requests.get("http://127.0.0.1:5000/")

	return 'Precio Actualizado'

# --- Define la direccion y los parametros de las operaciones ---
@BTC.route('/Script-BTC', methods=['POST'])
def script():
	status = mongo.db.Status
	scriptJson = request.json
	@app.after_response
	def afterSar():
		operationFilter = {"Operation-BTC": True}	
		Operation = status.find_one(operationFilter)


		if scriptJson['side'] == "BUY":
			
			print("\n --- Order -> " + str(scriptJson['side']) + " --- ")

			if Operation['status'] == True:
				if Operation['side'] == "BUY":
					print(" --- Operation is Already BUY --- \n")
				else:
					getUsers_cancel()

					if Operation['updatePending'] == True:
						print(" --- Update Pending --- \n")
						getUsers_update()

					orderPrice = scriptJson['close']
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"status": True, "side": "BUY", "entryPrice": orderPrice}})

					getUsers_create()
			else:
				if Operation['updatePending'] == True:
					print("Update Pending\n")
					getUsers_update()

				orderPrice = scriptJson['close']
				status.update_one(
					{"Operation-BTC": True},
					{"$set": {"status": True, "side": "BUY", "entryPrice": orderPrice}})

				getUsers_create()


		elif scriptJson['side'] == "SELL":

			print("\n --- Order -> " + str(scriptJson['side']) + " --- ")

			if Operation['status'] == True:
				if Operation['side'] == "SELL":
					print("Operation is Already SELL\n")
				else:
					getUsers_cancel()

					if Operation['updatePending'] == True:
						getUsers_update()

					orderPrice = scriptJson['close']
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"status": True, "side": "SELL", "entryPrice": orderPrice}})

					getUsers_create()
			else:
				if Operation['updatePending'] == True:
					getUsers_update()

				orderPrice = scriptJson['close']
				status.update_one(
					{"Operation-BTC": True},
					{"$set": {"status": True, "side": "SELL", "entryPrice": orderPrice}})
					
				getUsers_create()	


		else:
			print("Error Request")

	return 'Operacion Realizada'





# --- Crea Operaciones en base a los parametros ---
def getUsers_create():
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_create()
	lockThisFunction = True

	print("\n-------------------- Create -------------------- \n")

	bots = mongo.db.Bots
	pairFormat = {"pair": "BTCUSDT"}
	thisPairBot = bots.find(pairFormat)
	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True and thisBot['isEnabledforTrade'] == True:
			createOrders()
		else:
			pass

	print("\n-------------------- Create -------------------- \n")
	lockThisFunction = False
	
def createOrders():
	global issues, tradeAmount
	issues = "None"
	import time
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
			
			global order, issues, tradeAmount
			retrying = False
			thisOrder = False

			ticker = binance.fetch_ticker('BTC/BUSD')
			orderPrice1 = float(ticker['close'])
			orderPrice = orderPrice1
			tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

			#print("\n -- New Order Price: " + str(orderPrice) + " -- ")

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
			
			
			time.sleep(3)
			if (thisOrder == True) and (order['status'] == "open"):
				#print("\n -- Order Status: Open // Creating Limit Order...-- ")
				retrying = True
				thisOrder = False
				binance.cancel_all_orders('BTC/BUSD')
				createLimitOrderBinance()
			else:
				#print("\n -- Order Status: Close -- ")
				pass


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
			
			global order, issues, tradeAmount
			retrying = False
			thisOrder = False

			ticker = bybit.fetch_ticker('BTC/BUSD')
			orderPrice1 = float(ticker['close'])
			orderPrice = orderPrice1
			tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage'] ) / orderPrice )

			#print("\n -- New Order Price: " + str(orderPrice) + " -- ")

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
			
			
			time.sleep(3)
			if (thisOrder == True) and (order['status'] == "open"):
				#print("\n -- Order Status: Open // Creating Limit Order...-- ")
				retrying = True
				thisOrder = False
				bybit.cancel_all_orders('BTC/BUSD')
				createLimitOrderBybit()
			else:
				#print("\n -- Order Status: Close -- ")
				pass


		createLimitOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Invalid Exchange"
		
	bots = mongo.db.Bots	
	bots.update_one(
		{"_id": thisBot['_id']},
		{"$set": {"lastOrderAmount": tradeAmount}})

	dateTime = datetime.now()
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")
	bots.update(
		{"_id": thisBot['_id']},
		{"$push": 
			{"log":
		{
			"status": "Open", "side": Operation['side'], "dateOpen": date, "timeOpen": ctime, "dateClose": "-", "timeClose": "-", "amount": tradeAmount, "issuesOpen": issues, "issuesClose": "-"
		}}})

	print(" Bot: " + str(thisBot['exchangeConnection']['apiKey']) + "key created with '" + str(issues) + "' isues")





# --- Cancela Operaciones en base a los parametros ---
def getUsers_cancel():
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_cancel()
	lockThisFunction = True
	print("\n-------------------- CANCEL -------------------- \n")
	global thisBot
	bots = mongo.db.Bots
	operation = mongo.db.Status
	pairFormat = {"pair": "BTCUSDT",}
	thisPairBot = bots.find(pairFormat)

	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True and thisBot['isEnabledforTrade'] == True:
			cancelOrders()
		else:
			pass

	operation.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "entryPrice": 0.00}})
	lockThisFunction = False
	print("\n-------------------- CANCEL -------------------- \n")

def cancelOrders():
	global issues
	issues = ""
	import time
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


		createMarketOrderBybit()
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"

	bots = mongo.db.Bots
	dateTime = datetime.now()
	date = dateTime.strftime("%d/%m/%y")
	ctime = dateTime.strftime("%H:%M:%S")
	bots.update_one(
		{"_id": (thisBot['_id']), "log.status": "Open"},
		{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": ctime, "log.$.issuesClose": issues}})

	print(" Bot: " + str(thisBot['exchangeConnection']['apiKey']) + "key canceled with '" + str(issues) + "' isues")





# --- Revisa continuamente el estado de las cuentas en base a los parametros ---
def getUsers_check():
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		pass
	else:

		global thisBot
		pairFormat = {"pair": "BTCUSDT"}
		bots = mongo.db.Bots
		thisPairBot = bots.find(pairFormat)

		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)

		if Operation['status'] == True:
			for thisBot in thisPairBot:
				if thisBot['isEnabled'] == True and thisBot['isEnabledforTrade'] == True:
					checkOrders()
				else:
					pass
		else:
			print(" Not in Operation -- BTC -- ")

def checkOrders():
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
				dateTime = datetime.now()
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
				dateTime = datetime.now()
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
def getUsers_update():
	global lockThisFunction, thisBot
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_update()
	lockThisFunction = True

	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)

	if Operation['status'] == True:

		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"updatePending": True}})

	else:
		print("\n-------------------- UPDATE -------------------- \n")

		global thisBot
		bots = mongo.db.Bots
		pairFormat = {"pair": "BTCUSDT",}
		thisPairBot = bots.find(pairFormat)

		for thisBot in thisPairBot:
			if thisBot['isEnabled'] == True:
				updateBots()
			else:
				pass

		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"updatePending": False}})

	print("\n-------------------- UPDATE -------------------- \n")
	
	lockThisFunction = False

def updateBots():
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

		bots = mongo.db.Bots	
		bots.update_one(
			{"_id": thisBot['_id']},
			{"$set": {"tradeAmount": round(newTradeAmount, 2), "isEnabledforTrade": True}})

	
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

schedule.every(6).seconds.do(getUsers_check)
schedule.every().day.at("05:00").do(getUsers_update)

# -------------------- Schedule --------------------