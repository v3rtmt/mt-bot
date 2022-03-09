from flask import Blueprint, request, current_app as app
from bson.objectid import ObjectId
import time
import ccxt
from Mongo.extensions import mongo


ETH = Blueprint('ETH', __name__)


apiKey = ""
apiSecret = ""
userJson = ""
inOperation = ""
side = ""
stopLoss = 0

# --- Actualiza Hull en la Base de Datos ---
@ETH.route('/Hull-ETH', methods=['POST'])
def Hull():
	hull = mongo.db.Status
	
	if request.json['Hull-ETH'] == True:
		id = ""
		hull.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- Hull -> " + str(status) + " --- \n")
	else:
		print("Error en Hull")

	return 'Hull Actualizado'

# --- Actualiza Sar en la Base de Datos ---
@ETH.route('/Sar-ETH', methods=['POST'])
def Sar():
	
	sar = mongo.db.Status
	time.sleep(0.1)
	
	if request.json['Sar-ETH'] == True:
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

			sartpFilter = {"SarTP-ETH": True}	
			status = mongo.db.Status
			SarTP = status.find_one(sartpFilter)

			if side == "BUY":
			
				if SarTP == "BUY":
					pass
				elif SarTP == "SELL":
					getUsers_cancel()
				else:
					print("Error SarTP no declarado")

			elif side == "SELL":
				
				if SarTP == "SELL":
					pass
				elif SarTP == "BUY":
					getUsers_cancel()
				else:
					print("Error SarTP no declarado")

			else:
				print("Error Side no declarado")

		else:
			pass

	return 'Sar Actualizado'

# --- Actualiza SarTP en la Base de Datos ---
@ETH.route('/SarTP-ETH', methods=['POST'])
def SarTP():
	
	sartp = mongo.db.Status
	
	if request.json['SarTP-ETH'] == True:
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
			getUsers_cancel()
		else:
			pass

	return 'SarTP Actualizado'

# --- Recoge SniperSL (open ticker) como Stop Loss en las operaciones ---
@ETH.route('/SniperSL-ETH', methods=['POST'])
def SniperSL():

	global stopLoss	
	stopLoss = request.json['sl'] - 15

	return 'SniperSL Actualizado'

# --- Actualiza Sniper en la Base de Datos para confirmar operaciones---
@ETH.route('/Sniper-ETH', methods=['POST'])
def Sniper():
	
	sniper = mongo.db.Status
	time.sleep(0.2)
	
	if request.json['Sniper-ETH'] == True:
		id = ""
		sniper.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']  
		print("\n --- Sniper -> " + str(status) + " --- \n")
	else:
		print("Error en Sniper")

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
		"Sniper-ETH": True,
		"status": "NULL" 
	}

	# --- Filtros --- #

	hullFilter = {"Hull-ETH": True}
	sarFilter = {"Sar-ETH": True}
	sniperFilter = {"Sniper-ETH": True}

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

	bots = mongo.db.Bots
	pairFormat = {
		"pair": "ETHUSDT",
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

	binance = ccxt.binance({
		'apiKey': 'WlxQHeOJnGmHeqorhw8kWDNoa5i3GM6aoEFSKWLJTXI8jCUqMsksCdwOYjVgf8Ye',
		'secret': '1g3Prfet0ui4yLLxjVDCFT0PaRW3Yzq3DXalAcdqN0vhm9uRdnAUqmUWgnSVYA8g',
		'options': {
			'defaultType': 'future',
		},
	})
	while inOperation == True:
		price = binance.fetch_ticker('ETH/USDT')
		if side == "BUY":
			if price <= stopLoss:
				getUsers_cancel()
			else:
				pass
		elif side == "SELL":
			if price >= stopLoss:
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
				binance.create_market_buy_order('ETH/USDT', tradeAmount)
			elif side == "SELL":
				binance.create_market_sell_order('ETH/USDT', tradeAmount)
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
				bybit.create_market_buy_order('ETH/USDT', tradeAmount)
			elif side == "SELL":
				bybit.create_market_sell_order('ETH/USDT', tradeAmount)
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
		"pair": "ETHUSDT",
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
				binance.create_market_sell_order('ETH/USDT', tradeAmount, params={'reduce_only': True})
			elif side == "SELL":
				binance.create_market_buy_order('ETH/USDT', tradeAmount, params={'reduce_only': True})
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
				bybit.create_market_sell_order('ETH/USDT', tradeAmount, params={'reduce_only': True})
			elif side == "SELL":
				bybit.create_market_buy_order('ETH/USDT', tradeAmount, params={'reduce_only': True})
			else:
				print("ERROR SIDE (SIDE NO DECLARADA)")
		except:
			print("NO HAY POSICIONES ABIERTAS PARA ESTE USUARIO")
	else:
		print("ERROR EN BASE DE DATOS (EXCHANGE INVALIDO)")	
		