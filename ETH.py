from flask import Blueprint, request
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

# --- Actualiza Hull en la Base de Datos ---
@ETH.route('/Hull-ETH', methods=['POST'])
def Hull():
	hull = mongo.db.Status
	
	if request.json['Hull-ETH'] == True:
		id = "621b1a7717d2224fc51f5274"
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
		id = "621b1a7e17d2224fc51f5275"
		sar.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']
		print("\n --- Sar -> " + str(status) + " --- \n")
	else:
		print("Error en Sar")

	if inOperation == True:
		getUsers_cancel()
	else:
		pass

	return 'Sar Actualizado'

# --- Actualiza Sniper en la Base de Datos ---
@ETH.route('/Sniper-ETH', methods=['POST'])
def Sniper():
	
	sniper = mongo.db.Status
	time.sleep(0.2)
	
	if request.json['Sniper-ETH'] == True:
		id = "621b1a9917d2224fc51f5276"
		sniper.find_one_and_update(
			{'_id': ObjectId(id)}, {'$inc': {}, '$set': (request.json)}
			)
		status = request.json['status']  
		print("\n --- Sniper -> " + str(status) + " --- \n")
	else:
		print("Error en Sniper")

	execute()

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

			else:
				pass   
		else:
			pass	
	else:
		pass

	#----------------------------------------------------------------------------------

	id = "6210545703d15dd5a0b47432"
	status.find_one_and_update(
		{'_id': ObjectId(id)}, {'$inc': {}, '$set': (sniperNull)}
		)


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