from flask import Blueprint, render_template, request, current_app as app
from bson.objectid import ObjectId
import time
import ccxt
import datetime
from datetime import datetime
from Mongo.extensions import mongo

BTC = Blueprint('BTC', __name__)

lockThis = False
close = 0.00
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
				time.sleep(400)
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "SELL MOVEMENT":
				time.sleep(400)
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "BUY IMPULSE":
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			elif sqzmomJson['status'] == "SELL IMPULSE":
				sqzmom.update_one(
					{"SQZMOM-BTC": True},
					{"$set":{"status": sqzmomJson['status']}}
				)
				print("\n --- SQZMOM -> " + str(sqzmomJson['status']) + " --- \n")
			else:
				print("Valor de SQZMOM Erroneo")
		else:
			print("Error en SQZMOM")
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
			sartpFilter = {"SarTP-BTC": True}	
			status = mongo.db.Status
			SarTP = status.find_one(sartpFilter)
			if Operation['side'] == "BUY":
				if SarTP['status'] == "BUY":
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"sarTPcondition": True}}
					)
				elif SarTP['status'] == "SELL":
					getUsers_cancel()
			elif Operation['side'] == "SELL":
				if SarTP['status'] == "SELL":
					status.update_one(
						{"Operation-BTC": True},
						{"$set": {"sarTPcondition": True}}
					)
				elif SarTP['status'] == "BUY":
					getUsers_cancel()	
			else:
				print("\nError Side no declarado (After Sar)")
		else:
			pass
	return 'Sar Actualizado'

# --- Actualiza SarTP en la Base de Datos ---
@BTC.route('/SarTP-BTC', methods=['POST'])
def SarTP():
	sartp = mongo.db.Status
	if request.json['SarTP-BTC'] == True:
		sartp.update_one(
			{"SarTP-BTC": True},
			{"$set": {"status": request.json['status']}}
		)
		print("\n --- SartTP -> " + str(request.json['status']) + " --- \n")
	else:
		print("Error en SarTP")
	@app.after_response
	def afterSarTP():
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)
		if Operation['status'] == True:
			if Operation['sarTPcondition'] == True:
				status.update_one(
					{"Operation-BTC": True},
					{"$set": {"sarTPcondition": False}}
				)
				getUsers_cancel()
			else:
				pass
		else:
			pass
	return 'SarTP Actualizado'

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
		if Operation['recoil'] == 1:
			pass
		else:
			status.update_one(
				{"Operation-BTC": True},
				{"$set": {"entryPrice": close}}
			)
		if Operation['status'] == False:
			execute()
		else:
			pass
	return 'Sniper Actualizado'

@BTC.route('/Price-BTC', methods=['POST'])
def Price():
	price = mongo.db.Status
	if request.json['Price-BTC'] == True:
		price.update_one(
			{"Operation-BTC": True},
			{"$set": {"lastPrice": request.json['price']}}
		)
		print("\n --- Close Price -> " + str(request.json['price']) + " --- \n")
	else:
		print("Error en Price")
	@app.after_response
	def afterPrice():
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)
		if Operation['status'] == True:
			if Operation['side'] == "BUY":
				if Operation['lastPrice'] <= Operation['stopLoss']:
					getUsers_cancel()
				else:
					newStopLoss = (Operation['lastPrice'] - (Operation['lastPrice'] * 0.004))
					if newStopLoss > Operation['stopLoss']:
						status.update_one(
						{"Operation-BTC": True},
						{"$set": {"stopLoss": newStopLoss}}
						)
						print("\n --- Stop Loss -> " + str(newStopLoss) + " --- \n")
					else:
						pass
			elif Operation['side'] == "SELL":
				if Operation['lastPrice'] >= Operation['stopLoss']:
					getUsers_cancel()
				else:
					newStopLoss = (Operation['lastPrice'] + (Operation['lastPrice'] * 0.004))
					if newStopLoss < Operation['stopLoss']:
						status.update_one(
						{"Operation-BTC": True},
						{"$set": {"stopLoss": newStopLoss}}
						)
						print("\n --- Stop Loss -> " + str(newStopLoss) + " --- \n")
					else:
						pass
		else:
			pass
	return 'Precio Actualizado'







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

	if Operation['recoil'] == 0:
		if Squeeze['status'] == "ON":
			if Sqzmom['status'] == "BUY IMPULSE":
				if Hull['status'] == "BUY":
					if Sar['status'] == "BUY":
						if Sniper['status'] == "BUY":
							lockThis = False
							print("\n---------------BUY---------------\n")
							status.update_one(
								{"Operation-BTC": True},
								{"$set": {"status": True, "side": "BUY"}})
							stopLoss = (close - (close * 0.004))
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
								{"$set": {"status": True, "side": "SELL"}})
							stopLoss = (close + (close * 0.004))
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
				if Sqzmom['status'] == "BUY IMPULSE":
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
				if Sqzmom['status'] == "BUY IMPULSE":
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
			lockThis = False
			status.update_one(
				{"Sniper-BTC": True},
				{"$set": {"status": "Null"}})
	elif Operation['recoil'] == 2:
		if Sqzmom['status'] == "BUY IMPULSE":
			if Hull['status'] == "BUY":
				if Sar['status'] == "BUY":
					if Sniper['status'] == "BUY":
						lockThis = False
						print("\n---------------BUY---------------\n")
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"status": True, "side": "BUY"}})
						stopLoss = (close - (close * 0.004))
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": stopLoss}})
						print("\n --- Stop Loss -> " + str(stopLoss) + " --- \n")
						getUsers_create()
						status.update_one(
							{"Sniper-BTC": True},
							{"$set": {"status": "Null"}})
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"recoil": 0}})				
					else:
						pass
				else:
					pass
			else:
				pass
		else:
			pass
		if Sqzmom['status'] == "SELL IMPULSE":
			if Hull['status'] == "SELL":
				if Sar['status'] == "SELL":
					if Sniper['status'] == "SELL":
						lockThis = False
						print("\n---------------SELL---------------\n")
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"status": True, "side": "SELL"}})
						stopLoss = (close + (close * 0.004))
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"stopLoss": stopLoss}})
						print("\n --- Stop Loss -> " + str(stopLoss) + " --- \n")
						getUsers_create()
						status.update_one(
							{"Sniper-BTC": True},
							{"$set": {"status": "Null"}})
						status.update_one(
							{"Operation-BTC": True},
							{"$set": {"recoil": 0}})				
					else:
						pass   
				else:
					pass	
			else:
				pass
		else:
			pass
	else:
		status.update_one(
			{"Operation-BTC": True},
			{"$set": {"recoil": 2}})







def getUsers_create():
	global thisBot

	bots = mongo.db.Bots
	pairFormat = {"pair": "BTCUSDT"}
	thisPairBot = bots.find(pairFormat)
	for thisBot in thisPairBot:
		if thisBot['isEnabled'] == True:
			createOrders()
		else:
			pass
	print("\n-------------------- Create -------------------- ")
	
	#---------------------------------------- Trailing Stop Loss ----------------------------------------
	
	operationFilter = {"Operation-BTC": True}	
	status = mongo.db.Status
	Operation = status.find_one(operationFilter)

	while Operation['status'] == True:
		time.sleep(4)
		binance = ccxt.binance({
			'apiKey': 'WlxQHeOJnGmHeqorhw8kWDNoa5i3GM6aoEFSKWLJTXI8jCUqMsksCdwOYjVgf8Ye',
			'secret': '1g3Prfet0ui4yLLxjVDCFT0PaRW3Yzq3DXalAcdqN0vhm9uRdnAUqmUWgnSVYA8g',
			'options': {'defaultType': 'future',},})
	
		ticker = binance.fetch_ticker('BTC/USDT')
		currentPrice = float(ticker['close'])
		operationFilter = {"Operation-BTC": True}	
		status = mongo.db.Status
		Operation = status.find_one(operationFilter)
	
		if Operation['side'] == "BUY":
			if currentPrice <= Operation['stopLoss']:
				getUsers_cancel()
			else:
				pass
		elif Operation['side'] == "SELL":
			if currentPrice >= Operation['stopLoss']:
				getUsers_cancel()
			else:
				pass
		else:
			pass

def createOrders():
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
		ticker = binance.fetch_ticker('BTC/USDT')
		currentPrice = float(ticker['close'])
		balance = binance.fetch_balance()
		balanceUSDT = balance['USDT']['free']
		tradeAmount = ( ( thisBot['quantityLeverage'] * ( balanceUSDT * ( thisBot['tradeAmount'] / 100 ) ) ) / currentPrice )
		
		try:
			if Operation['side'] == "BUY":
				binance.create_market_buy_order('BTC/USDT', tradeAmount)
			elif Operation['side'] == "SELL":
				binance.create_market_sell_order('BTC/USDT', tradeAmount)
			else:
				print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
			issues = "None"
		except:
			issues = "Insufficient Funds"
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		
		bybit.enableRateLimit = True
		ticker = bybit.fetch_ticker('BTC/USDT')
		currentPrice = float(ticker['close'])
		balance = bybit.fetch_balance()
		balanceUSDT = balance['USDT']['free']
		tradeAmount = ( ( thisBot['quantityLeverage'] * ( balanceUSDT * ( thisBot['tradeAmount'] / 100 ) ) ) / currentPrice )
		try:
			if Operation['side'] == "BUY":
				bybit.create_market_buy_order('BTC/USDT', tradeAmount)
			elif Operation['side'] == "SELL":
				bybit.create_market_sell_order('BTC/USDT', tradeAmount)
			else:
				print("ERROR SIDE (SIDE NO DECLARADA) [EXCHANGE]")
			issues = "None"
		except:
			issues = "Insufficient Funds"
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Invalid Exchange"
		
	bots = mongo.db.Bots	
	bots.update_one(
		{"_id": thisBot['_id']},
		{"$set": {"lastOrderAmount": tradeAmount}})

	dateTime = datetime.now()
	date = dateTime.strftime("%d/%m/%y")
	time = dateTime.strftime("%H:%M:%S")
	bots.update(
		{"_id": thisBot['_id']},
		{"$push": 
			{"log":
		{
			"status": "Open", "side": Operation['side'], "dateOpen": date, "timeOpen": time, "dateClose": "-", "timeClose": "-", "amount": tradeAmount, "issues": issues
		}}})

def getUsers_cancel():
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

	binance = ccxt.binance({
			'apiKey': 'WlxQHeOJnGmHeqorhw8kWDNoa5i3GM6aoEFSKWLJTXI8jCUqMsksCdwOYjVgf8Ye',
			'secret': '1g3Prfet0ui4yLLxjVDCFT0PaRW3Yzq3DXalAcdqN0vhm9uRdnAUqmUWgnSVYA8g',
			'options': {'defaultType': 'future',},})
	
	ticker = binance.fetch_ticker('BTC/USDT')
	currentPrice = float(ticker['close'])
	operationFilter = {"Operation-BTC": True}	
	entryPrice = operation.find_one(operationFilter)

	if entryPrice['side'] == "BUY":
		onePercent = ( entryPrice['entryPrice'] + ( entryPrice['entryPrice'] * 0.01 ) )
		if currentPrice >= onePercent:
			operation.update_one(
				{"Operation-BTC": True},
				{"$set": {"recoil": 1}})
		else:
			pass
	elif entryPrice['side'] == "SELL":
		onePercent = ( entryPrice['entryPrice'] - ( entryPrice['entryPrice'] * 0.01 ) )
		if currentPrice <= onePercent:
			operation.update_one(
				{"Operation-BTC": True},
				{"$set": {"recoil": 1}})
		else:
			pass
	else:
		pass

	operation.update_one(
		{"Operation-BTC": True},
		{"$set": {"status": False, "side": "", "stopLoss": 0.00, "entryPrice": 0.00}})
	
	print("\n-------------------- CANCEL -------------------- ")

def cancelOrders():
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
		
		try:
			if Operation['side'] == "BUY":
				binance.create_market_sell_order('BTC/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			elif Operation['side'] == "SELL":
				binance.create_market_buy_order('BTC/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
			issues = "None"
		except:
			print("NO HAY POSICIONES ABIERTAS PARA ESTE USUARIO")
			issues = "No Orders Open"
	
	#-------------------- BYBIT --------------------
	elif thisBot['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (thisBot['exchangeConnection']['apiKey']),
			'secret': (thisBot['exchangeConnection']['apiSecret']),
			'options': {'defaultType': 'future',},})
		bybit.enableRateLimit = True
		
		try:
			if Operation['side'] == "BUY":
				bybit.create_market_sell_order('BTC/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			elif Operation['side'] == "SELL":
				bybit.create_market_buy_order('BTC/USDT', thisBot['lastOrderAmount'], params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
			issues = "None"
		except:
			print("NO HAY POSICIONES ABIERTAS PARA ESTE USUARIO")
			issues = "No Orders Open"
	
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		issues = "Data Error (Report with Admins)"

	bots = mongo.db.Bots
	dateTime = datetime.now()
	date = dateTime.strftime("%d/%m/%y")
	time = dateTime.strftime("%H:%M:%S")
	bots.update_one(
		{"_id": (thisBot['_id']), "log.status": "Open"},
		{"$set": {"log.$.status": "Close", "log.$.dateClose": date, "log.$.timeClose": time, "log.$.issues": issues}})
		
@BTC.route('/BTC', methods=['GET'])
def btc():
	binance = ccxt.binance({
		'apiKey': 'WlxQHeOJnGmHeqorhw8kWDNoa5i3GM6aoEFSKWLJTXI8jCUqMsksCdwOYjVgf8Ye',
		'secret': '1g3Prfet0ui4yLLxjVDCFT0PaRW3Yzq3DXalAcdqN0vhm9uRdnAUqmUWgnSVYA8g',
		'options': {'defaultType': 'future',},})
	binance.enableRateLimit = True
	ticker = binance.fetch_ticker('BTC/USDT')
	price = float(ticker['close'])
	status = mongo.db.Status

	squeezeFilter = {"Squeeze-BTC": True}
	sqzmomFilter = {"SQZMOM-BTC": True}
	hullFilter = {"Hull-BTC": True}
	sarFilter = {"Sar-BTC": True}
	sartpFilter = {"SarTP-BTC": True}
	operationFilter = {"Operation-BTC": True}

	SqueezeS = status.find_one(squeezeFilter)
	SqzmomS = status.find_one(sqzmomFilter)
	HullS = status.find_one(hullFilter)
	SarS = status.find_one(sarFilter)
	SarTPS = status.find_one(sartpFilter)
	OperationS = status.find_one(operationFilter)

	Squeeze = SqueezeS['status']
	Sqzmom = SqzmomS['status']
	Hull = HullS['status']
	Sar = SarS['status']
	SarTP = SarTPS['status']
	Operation = OperationS['status']
	Side = OperationS['side']
	StopL = OperationS['stopLoss']
	Recoil = OperationS['recoil']
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
	if SarTP == "BUY": SarTPColor = "success"
	else: SarTPColor = "danger"
	if Operation == True: OperationColor = "primary"
	else: OperationColor = "secondary"
	if StopL == 0.00: slColor = "secondary"
	else: slColor = "primary"
	if Side == "BUY": SideColor = "success"
	elif Side == "SELL": SideColor = "danger"
	else: SideColor = "secondary"
	if Recoil == 1: RecoilColor = "primary"
	elif Recoil == 2: RecoilColor = "primary"
	else: RecoilColor = "secondary"
	if EntryP == 0: epColor = "secondary"
	else: epColor = "primary"
	
	return render_template('bitcoin.html', 
	Squeeze=Squeeze,
	Sqzmom=Sqzmom,
	Hull=Hull,  
	Sar=Sar, 
	SarTP=SarTP, 
	Operation=Operation,
	StopL=StopL,
	Recoil=Recoil,
	SqueezeColor=SqueezeColor,
	SqzmomColor=SqzmomColor,
	HullColor=HullColor,
	SarColor=SarColor,
	SarTPColor=SarTPColor,
	OperationColor=OperationColor,
	slColor=slColor,
	Price=price,
	Side=Side,
	SideColor=SideColor,
	RecoilColor=RecoilColor,
	EntryP=EntryP,
	epColor=epColor)
