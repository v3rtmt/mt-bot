from flask import Blueprint, render_template, request, current_app as app
from bson.objectid import ObjectId
import time
import ccxt
import datetime
from datetime import datetime
from Mongo.extensions import mongo

BTC = Blueprint('BTC', __name__)

clock = [
	"447", "448", "449", "450", "451", "452", "453", "454", "455", "456", "457", "458", "459", "500",
	"947", "948", "949", "950", "951", "952", "953", "954", "955", "956", "957", "958", "959", "1000",
	"1447", "1448", "1449", "1450", "1451", "1452", "1453", "1454", "1455", "1456", "1457", "1458", "1459", "1500",
	"1947", "1948", "1949", "1950", "1951", "1952", "1953", "1954", "1955", "1956", "1957", "1958", "1959", "2000",
	"2447", "2448", "2449", "2450", "2451", "2452", "2453", "2454", "2455", "2456", "2457", "2458", "2459", "2500",
	"2947", "2948", "2949", "2950", "2951", "2952", "2953", "2954", "2955", "2956", "2957", "2958", "2959", "3000",
	"3447", "3448", "3449", "3450", "3451", "3452", "3453", "3454", "3455", "3456", "3457", "3458", "3459", "3500",
	"3947", "3948", "3949", "3950", "3951", "3952", "3953", "3954", "3955", "3956", "3957", "3958", "3959", "4000",
	"4447", "4448", "4449", "4450", "4451", "4452", "4453", "4454", "4455", "4456", "4457", "4458", "4459", "4500",
	"4947", "4948", "4949", "4950", "4951", "4952", "4953", "4954", "4955", "4956", "4957", "4958", "4959", "5000",
	"5447", "5448", "5449", "5450", "5451", "5452", "5453", "5454", "5455", "5456", "5457", "5458", "5459", "5500",
	"5947", "5948", "5949", "5950", "5951", "5952", "5953", "5954", "5955", "5956", "5957", "5958", "5959", "0000"
]

orderPrice = 0.00
lockThis = False
order = ""
issues = ""
lockThisFunction = False
tradeAmount = 0.0
# --- Actualiza Squeeze Momentum en la Base de Datos ---
@BTC.route('/Squeeze-BTC', methods=['POST'])
def Squeeze():
	squeeze = mongo.db.Status
	if request.json['Squeeze-BTC'] == True:
		squeeze.update_one(
			{"Squeeze-BTC": True},
			{"$set": {"status": request.json['status']}}
		)
		print("\n --- Squeeze -> " + str(request.json['status']) + " --- \n")
	else:
		print("Error en Squeeze")
	return 'Squeeze Actualizado'

# --- Actualiza SQZMOM Status en la Base de Datos ---
@BTC.route('/Sqzmom-BTC', methods=['POST'])
def Sqzmom():
	global sqzmomJson
	sqzmomJson = request.json

	@app.after_response
	def afterSqzmom():
		sqzmom = mongo.db.Status
		if sqzmomJson['SQZMOM-BTC'] == True:
			if sqzmomJson['status'] == "BUY MOVEMENT":
				time.sleep(15)	
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}	# Si SQZMOM actualiza a MOVEMENT espera 15s a la siguiente vela
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "SELL MOVEMENT":
				time.sleep(15)
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}	# Si SQZMOM actualiza a MOVEMENT espera 15s a la siguiente vela
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "BUY IMPULSE":
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}	# IMPULSE se actualiza en vela actual
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "SELL IMPULSE":
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}	# IMPULSE se actualiza en vela actual
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			else:
				print("Valor de SQZMOM Erroneo")
		else:
			print("Error en SQZMOM")

		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)

		if sqzmomJson['status'] == "BUY IMPULSE":
			if Operation['status'] == True:
				status.update_one(
					{"Operation-BTC": True},
					{"$set":{"impulseCondition": True}}		# IMPULSE implica que la operacion vaya disminuyendo
				)											# Stop Loss hasta conseguir la venta del contrato
				print("\n --- ImpulseC -> True --- \n")		
			else:											
				pass

		elif sqzmomJson['status'] == "SELL IMPULSE":
			if Operation['status'] == True:
				status.update_one(
					{"Operation-BTC": True},
					{"$set":{"impulseCondition": True}}		# IMPULSE implica que la operacion vaya disminuyendo
				)											# Stop Loss hasta conseguir la venta del contrato
				print("\n --- ImpulseC -> True --- \n")
			else:											
				pass

		else:
			pass

	return 'SQZMOM Actualizado'

# --- Actualiza Hull en la Base de Datos ---
@BTC.route('/Hull-BTC', methods=['POST'])
def Hull():
	hull = mongo.db.Status
	if request.json['Hull-BTC'] == True:
		hull.update_one(
			{"Hull-BTC": True},
			{"$set": {"status": request.json['status']}}
		)
		print("\n --- Hull -> " + str(request.json['status']) + " --- \n")
	else:
		print("Error en Hull")
	return 'Hull Actualizado'

# --- Actualiza Sar en la Base de Datos ---
@BTC.route('/Sar-BTC', methods=['POST'])
def Sar():
	sar = mongo.db.Status
	if request.json['Sar-BTC'] == True:
		sar.update_one(
			{"Sar-BTC": True},
			{"$set": {"status": request.json['status']}}
		)
		print("\n --- Sar -> " + str(request.json['status']) + " --- \n")
	else:
		print("Error en Sar")

	@app.after_response
	def afterSar():

		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)

		if Operation['status'] == True:
			getUsers_cancel()	# Cancelar todas las operaciones si Sar cambia de tendecia
		else:
			pass

	return 'Sar Actualizado'

# --- Actualiza Sniper en la Base de Datos para confirmar operaciones---
@BTC.route('/Sniper-BTC', methods=['POST'])
def Sniper():
	sniper = mongo.db.Status
	time.sleep(2)
	if request.json['Sniper-BTC'] == True:
		sniper.update_one(
			{"Sniper-BTC": True},
			{"$set": {"status": request.json['status']}}
		)
		print("\n --- Sniper -> " + str(request.json['status']) + " --- \n")
		global close
		close = request.json['close']
		close = close - 15
		sniper.update_one(
			{"Operation-BTC": True},
			{"$set": {"lastPrice": close}}
		)
	else:
		print("Error en Sniper")

	@app.after_response
	def afterSniper():
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)
		if Operation['status'] == False:
			execute()			# Ejecuta las operaciones si todas las condiciones se cumplen
		else:
			pass
	return 'Sniper Actualizado'

@BTC.route('/Price-BTC', methods=['POST'])
def Price():
	
	priceJson = request.json

	@app.after_response
	def afterPrice():
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)

		if Operation['status'] == True:
			if Operation['side'] == "BUY":
				if priceJson['price'] <= Operation['stopLoss']:
					getUsers_cancelMarket()
				else:
					newStopLoss = (priceJson['price'] - Operation['trail'])
					if newStopLoss > Operation['stopLoss']:
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": newStopLoss}}
						)
						print("\n --- Stop Loss -> " + str(newStopLoss) + " --- \n")
					else:
						pass

			elif Operation['side'] == "SELL":
				if priceJson['price'] >= Operation['stopLoss']:
					getUsers_cancelMarket()
				else:
					newStopLoss = (priceJson['price'] + Operation['trail'])
					if newStopLoss < Operation['stopLoss']:
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": newStopLoss}}
						)
						print("\n --- Stop Loss -> " + str(newStopLoss) + " --- \n")
					else:
						pass
		else:
			print("\n --- Price not in Operation --- \n")

	return 'Precio Actualizado'

@BTC.route('/Script-BTC', methods=['POST'])
def script():
	status = mongo.db.Status
	scriptJson = request.json
	@app.after_response
	def afterSar():
		operationFilter = {"Operation-BTC": True}	
		Operation = status.find_one(operationFilter)

		if scriptJson['side'] == "BUY":
			stopLoss = (scriptJson['close'] - (scriptJson['close'] * 0.005))
			trail = scriptJson['close'] - stopLoss
			tp = scriptJson['close'] - scriptJson['lowest']
			takeProfit = scriptJson['close'] + (tp * 2)
			
			print("\n --- Order -> " + str(scriptJson['side']) + " --- ")
			print("\n --- StopLoss -> " + str(stopLoss) + " --- ")
			print("\n --- TakeProfit -> " + str(takeProfit) + " --- ")

			if Operation['status'] == True:
				if Operation['side'] == "BUY":
					pass
				else:
					getUsers_cancel()
					orderPrice = scriptJson['close']
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"status": True, "side": "BUY", "entryPrice": orderPrice, "stopLoss": stopLoss, "takeProfit": takeProfit, "trail": trail}})
					getUsers_create()
			else:
				orderPrice = scriptJson['close']
				status.update_one(
					{"Operation-BTC": True},
					{"$set": {"status": True, "side": "BUY", "entryPrice": orderPrice, "stopLoss": stopLoss, "takeProfit": takeProfit, "trail": trail}})
				getUsers_create()



		elif scriptJson['side'] == "SELL":
			stopLoss = (scriptJson['close'] + (scriptJson['close'] * 0.005))
			trail = scriptJson['close'] + stopLoss
			tp = scriptJson['highest'] - scriptJson['close']
			takeProfit = scriptJson['close'] - (tp * 2)

			print("\n --- Order -> " + str(scriptJson['side']) + " --- ")
			print("\n --- StopLoss -> " + str(stopLoss) + " --- ")
			print("\n --- TakeProfit -> " + str(takeProfit) + " --- ")

			if Operation['status'] == True:
				if Operation['side'] == "SELL":
					pass
				else:
					getUsers_cancel()
					orderPrice = scriptJson['close']
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"status": True, "side": "SELL", "entryPrice": orderPrice, "stopLoss": stopLoss, "takeProfit": takeProfit, "trail": trail}})
					getUsers_create()
			else:
				orderPrice = scriptJson['close']
				status.update_one(
					{"Operation-BTC": True},
					{"$set": {"status": True, "side": "SELL", "entryPrice": orderPrice, "stopLoss": stopLoss, "takeProfit": takeProfit, "trail": trail}})
				getUsers_create()	



		else:
			print("Error Request")

	return 'Operacion Realizada'





def execute():
	global lockThis, close
	status = mongo.db.Status
	squeezeFilter = {"Squeeze-BTC": True}
	sqzmomFilter = {"SQZMOM-BTC": True}
	hullFilter = {"Hull-BTC": True}
	sarFilter = {"Sar-BTC": True}
	sniperFilter = {"Sniper-BTC": True}
	operationFilter = {"Operation-BTC": True}
	Squeeze = status.find_one(squeezeFilter)
	Sqzmom = status.find_one(sqzmomFilter)
	Hull = status.find_one(hullFilter)
	Sar = status.find_one(sarFilter)
	Sniper = status.find_one(sniperFilter)
	Operation = status.find_one(operationFilter)

	
	if Squeeze['status'] == "ON":
		if Sqzmom['status'] == "BUY IMPULSE":
			if Hull['status'] == "BUY":
				if Sar['status'] == "BUY":
					if Sniper['status'] == "BUY":
						lockThis = False
						print("\n---------------BUY---------------\n")
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"status": True, "side": "BUY", "entryPrice": close}})
						stopLoss = (close - (close * 0.003))
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": stopLoss}})
						print("\n --- Stop Loss -> " + str(stopLoss) + " --- \n")
						getUsers_create()
						status.update_one(
							{"Sniper-BTC": True},
							{"$set": {"status": "Null"}})				
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
	else:
		pass
	if Squeeze['status'] == "ON":
		if Sqzmom['status'] == "SELL IMPULSE":
			if Hull['status'] == "SELL":
				if Sar['status'] == "SELL":
					if Sniper['status'] == "SELL":
						lockThis = False
						print("\n---------------SELL---------------\n")
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"status": True, "side": "SELL", "entryPrice": close}})
						stopLoss = (close + (close * 0.003))
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": stopLoss}})
						print("\n --- Stop Loss -> " + str(stopLoss) + " --- \n")
						getUsers_create()
						status.update_one(
							{"Sniper-BTC": True},
							{"$set": {"status": "Null"}})				
					else:
						pass   
				else:
					pass	
			else:
				pass
		else:
			pass
	else:
		pass
	if lockThis == False:
		if Squeeze['status'] == "ON":
			if Sqzmom['status'] == "BUY IMPULSE":
				if Hull['status'] == "BUY":
					if Sniper['status'] == "BUY":
						if Sar['status'] == "SELL":
							print("Waiting for SAR")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
		if Squeeze['status'] == "ON":
			if Sqzmom['status'] == "SELL IMPULSE":
				if Hull['status'] == "SELL":
					if Sniper['status'] == "SELL":
						if Sar['status'] == "BUY":
							print("Waiting for SAR")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
	else:
		pass
	if lockThis == False:
		if Squeeze['status'] == "OFF":
			if Sqzmom['status'] == "BUY IMPULSE":
				if Hull['status'] == "BUY":
					if Sniper['status'] == "BUY":
						if Sar['status'] == "BUY":
							print("Waiting for Squeeze")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
		if Squeeze['status'] == "OFF":
			if Sqzmom['status'] == "SELL IMPULSE":
				if Hull['status'] == "SELL":
					if Sniper['status'] == "SELL":
						if Sar['status'] == "SELL":
							print("Waiting for Squeeze")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
	else:
		pass
	if lockThis == False:
		if Squeeze['status'] == "ON":
			if Sqzmom['status'] == "BUY IMPULSE":
				if Hull['status'] == "SELL":
					if Sniper['status'] == "BUY":
						if Sar['status'] == "BUY":
							print("Waiting for Squeeze")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
		if Squeeze['status'] == "ON":
			if Sqzmom['status'] == "SELL IMPULSE":
				if Hull['status'] == "BUY":
					if Sniper['status'] == "SELL":
						if Sar['status'] == "SELL":
							print("Waiting for Squeeze")
							lockThis = True
							time.sleep(301)
							execute()
						else:
							pass
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
	else:
		lockThis = False
	status.update_one(
		{"Sniper-BTC": True},
			{"$set": {"status": "Null"}})







def getUsers_create():
	global lockThisFunction
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_create()
	lockThisFunction = True
	global thisBot
	print("\n-------------------- Create -------------------- ")
	bots = mongo.db.Bots
	pairFormat = {"pair": "BTCUSDT"}
	thisPairBot = bots.find(pairFormat)
	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True:
			createOrders()
		else:
			pass
	print("\n-------------------- Create -------------------- ")
	lockThisFunction = False
	#---------------------------------------- Trailing Stop Loss ----------------------------------------
	
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)

	while Operation['status'] == True:
		time.sleep(4)
		binance = ccxt.binance({
			'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
			'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
			'options': {'defaultType': 'future',},})
	
		ticker = binance.fetch_ticker('BTC/BUSD')
		currentPrice = float(ticker['close'])
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)
	
		if Operation['side'] == "BUY":
			if currentPrice <= Operation['stopLoss']:
				print("\n --- BUY:   Stop Loss Crossover--- \n")
				getUsers_cancelMarket()
			else:
				pass
			if currentPrice >= Operation['takeProfit']:
				print("\n --- BUY:   Take Profit Crossover--- \n")
				getUsers_cancelMarket()
			else:
				pass
		elif Operation['side'] == "SELL":
			if currentPrice >= Operation['stopLoss']:
				print("\n --- SELL:   Stop Loss Crossover--- \n")
				getUsers_cancelMarket()
			else:
				pass
			if currentPrice <= Operation['takeProfit']:
				print("\n --- SELL:   Take Profit Crossover--- \n")
				getUsers_cancelMarket()
			else:
				pass
		else:
			pass

def createOrders():
	global issues, tradeAmount
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
		
		def createLimitOrderBinance():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues, tradeAmount
			retrying = False
			thisOrder = False

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if 1>0:
				print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Limit Order")
				ticker = binance.fetch_ticker('BTC/BUSD')
				orderPrice1 = float(ticker['close'])
				orderPrice = orderPrice1
				tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage']) / orderPrice)
				print("\n -- Order Price: " + str(orderPrice) + " -- ")

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
						retrying == False
						thisOrder = False
					else:
						issues = "Insufficients founds"
						thisOrder = False
			else:
				print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Retrying")
				time.sleep(1)
				createLimitOrderBinance()	
			time.sleep(3)
			if (thisOrder == True) and (order['status'] == "open"):
				print("\n -- Order Status: Open -- ")
				print("\n -- Creating Limit Order... -- ")
				retrying = True
				thisOrder = False
				binance.cancel_all_orders('BTC/BUSD')
				createLimitOrderBinance()
			else:
				print("\n -- Order Status: Close -- ")

		print("this is a test")
		createLimitOrderBinance()
		
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True

		ticker = bybit.fetch_ticker('BTC/BUSD')
		currentPrice = float(ticker['close'])
		tradeAmount = ( ( thisBot['tradeAmount'] * thisBot['quantityLeverage']) / currentPrice)
		
		try:
			def createLimitOrderBybit():
				global order, issues

				orderTime1 = time.localtime()
				orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

				if orderTime in clock:
					print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Market Order")

					try:
						if Operation['side'] == "BUY":
							binance.create_market_buy_order('BTC/BUSD', tradeAmount)
						elif Operation['side'] == "SELL":
							binance.create_market_sell_order('BTC/BUSD', tradeAmount)
						else:
							print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
					except:
						issues = "Insufficients founds"

				else:
					print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Limit Order")
					ticker = binance.fetch_ticker('BTC/BUSD')
					orderPrice = float(ticker['close'])
					print("\n -- Order Price: " + str(orderPrice) + " -- ")

					try:
						if Operation['side'] == "BUY":
							order = binance.create_limit_buy_order('BTC/BUSD', tradeAmount, orderPrice)
						elif Operation['side'] == "SELL":
							order = binance.create_limit_sell_order('BTC/BUSD', tradeAmount, orderPrice)
						else:
							print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
					except:
						issues = "Insufficients founds"

				time.sleep(12)
				print("\n -- Order Status: " + order['status'] + " -- ")
				if order['status'] == "open":
					print("\n -- Creating New Order... -- ")
					binance.cancel_all_orders('BTC/BUSD')
					createLimitOrderBybit()
				issues = "None"

			createLimitOrderBybit()
		except:
			issues = "Insufficients founds"
	
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






def getUsers_cancel():
	global lockThisFunction
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_create()
	lockThisFunction = True
	print("\n-------------------- CANCEL -------------------- ")
	global thisBot
	bots = mongo.db.Bots
	operation = mongo.db.Status
	pairFormat = {"pair": "BTCUSDT",}
	thisPairBot = bots.find(pairFormat)

	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True:
			cancelOrders()
		else:
			pass

	operation.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "stopLoss": 0.00, "entryPrice": 0.00, "trail": 0.0, "takeProfit": 0.00}})
	lockThisFunction = False
	print("\n-------------------- CANCEL -------------------- ")

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

			if orderTime in clock:
				print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Market Order")

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
				print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Retrying")
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
		
		try:
			if Operation['side'] == "BUY":
				bybit.create_market_sell_order('ETH/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			if Operation['side'] == "SELL":
				bybit.create_market_buy_order('ETH/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			issues = "No orders open"
	
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





def getUsers_cancelMarket():
	global lockThisFunction
	if lockThisFunction == True:
		time.sleep(2)
		getUsers_create()
	lockThisFunction = True
	print("\n-------------------- CANCEL MARKET-------------------- ")
	global thisBot
	bots = mongo.db.Bots
	operation = mongo.db.Status
	pairFormat = {"pair": "BTCUSDT",}
	thisPairBot = bots.find(pairFormat)

	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True:
			cancelOrdersMarket()
		else:
			pass

	operation.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "stopLoss": 0.00, "entryPrice": 0.00, "trail": 0.0, "takeProfit": 0.00}})
	lockThisFunction = False
	print("\n-------------------- CANCEL MARKET-------------------- ")

def cancelOrdersMarket():
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
		
		def cancelMarketOrderBinance():
			operationFilter = {"Operation-BTC": True}	
			status = mongo.db.Status
			Operation = status.find_one(operationFilter)
			
			global order, issues

			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			print("\n -- Time: " + str(orderTime1.tm_min) + ":" + str(orderTime1.tm_sec) + " --> Market Order")

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


		cancelMarketOrderBinance()
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		
		try:
			if Operation['side'] == "BUY":
				bybit.create_market_sell_order('ETH/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			if Operation['side'] == "SELL":
				bybit.create_market_buy_order('ETH/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			issues = "No orders open"
	
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

	squeezeFilter = {"Squeeze-BTC": True}
	sqzmomFilter = {"SQZMOM-BTC": True}
	hullFilter = {"Hull-BTC": True}
	sarFilter = {"Sar-BTC": True}
	operationFilter = {"Operation-BTC": True}

	SqueezeS = status.find_one(squeezeFilter)
	SqzmomS = status.find_one(sqzmomFilter)
	HullS = status.find_one(hullFilter)
	SarS = status.find_one(sarFilter)
	OperationS = status.find_one(operationFilter)

	Squeeze = SqueezeS['status']
	Sqzmom = SqzmomS['status']
	Hull = HullS['status']
	Sar = SarS['status']
	Operation = OperationS['status']
	Side = OperationS['side']
	StopL = OperationS['stopLoss']
	EntryP = OperationS['entryPrice']
	
	if Squeeze == "ON": SqueezeColor = "primary"
	else: SqueezeColor = "secondary"
	if Sqzmom == "BUY IMPULSE": SqzmomColor = "success"
	elif Sqzmom == "BUY MOVEMENT": SqzmomColor = "success"
	elif Sqzmom == "SELL MOVEMENT": SqzmomColor = "danger"
	else: SqzmomColor = "danger"
	if Hull == "BUY": HullColor = "success"
	else: HullColor = "danger"
	if Sar == "BUY": SarColor = "success"
	else: SarColor = "danger"
	if Operation == True: OperationColor = "primary"
	else: OperationColor = "secondary"
	if StopL == 0.00: slColor = "secondary"
	else: slColor = "primary"
	if Side == "BUY": SideColor = "success"
	elif Side == "SELL": SideColor = "danger"
	else: SideColor = "secondary"
	if EntryP == 0: epColor = "secondary"
	else: epColor = "primary"
	
	return render_template('bitcoin.html', 
	Squeeze=Squeeze,
	Sqzmom=Sqzmom,
	Hull=Hull,  
	Sar=Sar, 
	Operation=Operation,
	StopL=StopL,
	SqueezeColor=SqueezeColor,
	SqzmomColor=SqzmomColor,
	HullColor=HullColor,
	SarColor=SarColor,
	OperationColor=OperationColor,
	slColor=slColor,
	Price=price,
	Side=Side,
	SideColor=SideColor,
	EntryP=EntryP,
	epColor=epColor)

@BTC.route('/time', methods=['GET'])
def ptime():
	status = mongo.db.Status
	status.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "stopLoss": 0.00, "entryPrice": 0.00, "trail": 0.0, "takeProfit": 0.00}})
	return "time"