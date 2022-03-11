from flask import Blueprint, request, current_app as app
from bson.objectid import ObjectId
import time
import ccxt
import datetime
from Mongo.extensions import mongo


BTC = Blueprint('BTC', __name__)


apiKey = ""
apiSecret = ""
userJson = ""
inOperation = ""
sarTPcondition = ""
side = ""
stopLoss = 0

# --- Actualiza Hull en la Base de Datos ---
@BTC.route('/Hull-BTC', methods=['POST'])
def Hull():
	hull = mongo.db.Status
	
	if request.json['Hull-BTC'] == True:
		id = ""
		hull.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- Hull -> " + str(status) + " --- \n")
	else:
		print("Error en Hull")

	return 'Hull Actualizado'

# --- Actualiza HullTrend en la Base de Datos ---
@BTC.route('/HullTrend-BTC', methods=['POST'])
def HullTrend():
	hullTrend = mongo.db.Status
	
	if request.json['HullTrend-BTC'] == True:
		id = ""
		hullTrend.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- HullTrend -> " + str(status) + " --- \n")
	else:
		print("Error en HullTrend")

	return 'HullTrend Actualizado'

# --- Actualiza Sar en la Base de Datos ---
@BTC.route('/Sar-BTC', methods=['POST'])
def Sar():
	global sarTPcondition

	sar = mongo.db.Status
	time.sleep(0.1)
	
	if request.json['Sar-BTC'] == True:
		id = ""
		sar.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- Sar -> " + str(status) + " --- \n")
	else:
		print("Error en Sar")

	@app.after_response
	def afterSar():
		if inOperation == True:

			sartpFilter = {"SarTP-BTC": True}	
			status = mongo.db.Status
			SarTP = status.find_one(sartpFilter)

			hullTrendFilter = {"HullTrend-BTC": True}	
			status = mongo.db.Status
			HullTrend = status.find_one(hullTrendFilter)

			if side == "BUY":
			
				if HullTrend == "BUY":

					if SarTP == "BUY":
						sarTPcondition = True

					elif SarTP == "SELL":
						getUsers_cancel()

				elif HullTrend == "SELL":
					getUsers_cancel()

				else:
					print("Error HullTrend no declarado")

			elif side == "SELL":
				
				if HullTrend == "SELL":

					if SarTP == "SELL":
						sarTPcondition = True

					elif SarTP == "BUY":
						getUsers_cancel()

				elif HullTrend == "BUY":
					getUsers_cancel()

				else:
					print("Error HullTrend no declarado")

			else:
				print("Error Side no declarado")

		else:
			pass

	return 'Sar Actualizado'

# --- Actualiza SarTP en la Base de Datos ---
@BTC.route('/SarTP-BTC', methods=['POST'])
def SarTP():
	
	sartp = mongo.db.Status
	
	if request.json['SarTP-BTC'] == True:
		id = ""
		sartp.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- SarTP -> " + str(status) + " --- \n")
	else:
		print("Error en SarTP")

	@app.after_response
	def afterSarTP():
		if inOperation == True:
			if sarTPcondition == True:
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
	time.sleep(0.2)
	
	if request.json['Sniper-BTC'] == True:
		id = ""
		sniper.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']  
		print("\n --- Sniper -> " + str(status) + " --- \n")
	else:
		print("Error en Sniper")

	global stopLoss	
	stopLoss = request.json['sl'] - 15

	@app.after_response
	def afterSniper():
		if inOperation == False:
			execute()
		else:
			pass

	return 'Sniper Actualizado'






def execute():

	global side

	status = mongo.db.Status

	sniperNull = {
		"Sniper-BTC": True,
		"status": "NULL" 
	}

	# --- Filtros --- #

	hullFilter = {"Hull-BTC": True}
	sarFilter = {"Sar-BTC": True}
	sniperFilter = {"Sniper-BTC": True}

	Hull = status.find_one(hullFilter)
	Sar = status.find_one(sarFilter)
	Sniper = status.find_one(sniperFilter)

	#----------------------------------------------------------------------------------

	if Hull['status'] == "BUY":
		if Sar['status'] == "BUY":
			if Sniper['status'] == "BUY":
 
				print("\n---------------BUY---------------\n")
				side = "BUY"
				getUsers_create()

				id = "id"
				status.find_one_and_update(
				{'_id': ObjectId(id)}, {'$inc': {}, '$set': (sniperNull)}
				)

			else:
				pass
		else:
			pass
	else:
		pass

	#----------------------------------------------------------------------------------

	if Hull['status'] == "SELL":
		if Sar['status'] == "SELL":
			if Sniper['status'] == "SELL":

				print("\n---------------SELL---------------\n")
				side = "SELL"
				getUsers_create()

				id = "id"
				status.find_one_and_update(
				{'_id': ObjectId(id)}, {'$inc': {}, '$set': (sniperNull)}
				)

			else:
				pass   
		else:
			pass	
	else:
		pass

	#----------------------------------------------------------------------------------

	if Hull['status'] == "BUY":
		if Sniper['status'] == "BUY":
			if Sar['status'] == "SELL":
				print("Waiting for SAR")
				time.sleep(901)
				execute()
			else:
				pass
		else:
			pass
	else:
		pass
	
	#----------------------------------------------------------------------------------

	if Hull['status'] == "SELL":
		if Sniper['status'] == "SELL":
			if Sar['status'] == "BUY":
				print("Waiting for SAR")
				time.sleep(901)
				execute()
			else:
				pass
		else:
			pass
	else:
		pass


#----------------------------------------------------------------------------------






def getUsers_create():

	global apiKey, apiSecret, userJson, tradeAmount

	# --- Busca todos los Bots correspondientes al par para ejecutar las operaciones ---

	bots = mongo.db.Bots
	pairFormat = {
		"pair": "BTCUSDT",
	}
	pairBot = bots.find(pairFormat)

	for user in pairBot:
		userJson = user
		apiKey = user['exchangeConnection']['apiKey']
		apiSecret = user['exchangeConnection']['apiSecret']
		tradeAmount = user['tradeAmount'] * user['quantityLeverage']
		createOrders()

	global inOperation
	inOperation = True

	
	# --- Inserta la operacion dentro de la coleccion Log ---

	datetime_object = datetime.datetime.now()

	logOrder = {
		"open": "open",
		"datetime": datetime_object,
		"side": side
	}
	
	log = mongo.db.Log
	log.insert_one(logOrder)
	
	print("\n-------------------- BUY -------------------- ")

	# --- Verifica que el precio no alcance el Stop Loss ---
	# --- Si esta precio lo alcanza cancela todas las operaciones ---

	binance = ccxt.binance({
		'apiKey': 'WlxQHeOJnGmHeqorhw8kWDNoa5i3GM6aoEFSKWLJTXI8jCUqMsksCdwOYjVgf8Ye',
		'secret': '1g3Prfet0ui4yLLxjVDCFT0PaRW3Yzq3DXalAcdqN0vhm9uRdnAUqmUWgnSVYA8g',
		'options': {
			'defaultType': 'future',
		},
	})

	stopLossOp = stopLoss

	while inOperation == True:
		price = binance.fetch_ticker('BTC/USDT')
		if side == "BUY":
			if price <= stopLossOp:
				getUsers_cancel()
			else:
				pass
		elif side == "SELL":
			if price >= stopLossOp:
				getUsers_cancel()
			else:
				pass
		else:
			pass


def createOrders():
	#-------------------- BINANCE -------------------- 
	if userJson['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {
				'defaultType': 'future',
			},
		})
		try:
			if side == "BUY":
				pass#testbinance.create_market_buy_order('BTC/USDT', tradeAmount)
			elif side == "SELL":
				pass#testbinance.create_market_sell_order('BTC/USDT', tradeAmount)
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			print("Fondos Insuficientes")

	#-------------------- BYBIT --------------------
	elif userJson['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {
				'defaultType': 'future',
			},
		})
		try:
			if side == "BUY":
				pass#testbybit.create_market_buy_order('BTC/USDT', tradeAmount)
			elif side == "SELL":
				pass#testbybit.create_market_sell_order('BTC/USDT', tradeAmount)
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			print("FONDOS INSUFICIENTES")
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	


#----------------------------------------------------------------------------------


def getUsers_cancel():

	global apiKey, apiSecret, userJson, tradeAmount

	bots = mongo.db.Bots
	pairFormat = {
		"pair": "BTCUSDT",
	}
	pairBot = bots.find(pairFormat)

	for user in pairBot:
		userJson = user
		apiKey = user['exchangeConnection']['apiKey']
		apiSecret = user['exchangeConnection']['apiSecret']
		tradeAmount = user['tradeAmount'] * user['quantityLeverage']
		cancelOrders()

	global inOperation
	inOperation = False

	# --- Inserta la cancelacion dentro de la coleccion Log ---

	datetime_object = datetime.datetime.now()

	logOrder = {
		"close": "close",
		"datetime": datetime_object,
		"side": side
	}
	
	log = mongo.db.Log
	log.insert_one(logOrder)

	print("\n-------------------- SELL -------------------- ")

def cancelOrders():
	#-------------------- BINANCE -------------------- 
	if userJson['exchange'] == "Binance":
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {
				'defaultType': 'future',
			},
		})
		try:
			if side == "BUY":
				pass#testbinance.create_market_sell_order('BTC/USDT', tradeAmount, params={'reduce_only': True})
			elif side == "SELL":
				pass#testbinance.create_market_buy_order('BTC/USDT', tradeAmount, params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			print("NO HAY POSICIONES ABIERTAS PARA ESTE USUARIO")

	#-------------------- BYBIT --------------------
	elif userJson['exchange'] == "Bybit":
		bybit = ccxt.bybit({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {
				'defaultType': 'future',
			},
		})
		try:
			if side == "BUY":
				pass#testbybit.create_market_sell_order('BTC/USDT', tradeAmount, params={'reduce_only': True})
			elif side == "SELL":
				pass#testbybit.create_market_buy_order('BTC/USDT', tradeAmount, params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			print("NO HAY POSICIONES ABIERTAS PARA ESTE USUARIO")
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		