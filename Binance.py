from datetime import datetime, timedelta, timezone
import random
import string
import ccxt

def order(bot, request):
	
	# Abrir ordenes de compra
	if request['action'] == "Buy":
		try:
			lastOrder = bot['log'][-1]

			if lastOrder['side'] == "Buy" and lastOrder['status'] == "Open":
				order = errorDetails("Buy", bot, "Ya existe actualmente una posición de compra abierta")
    
			elif lastOrder['status'] == "Open":
				order = errorDetails("Buy", bot, "Se requiere cerrar la posición de venta actual para abrir una nueva")
    
			else:
				order = createOrder("Buy", bot)
		except:
			order = createOrder("Buy", bot)



	# Abrir ordenes de venta
	elif request['action'] == "Sell":
		try:
			lastOrder = bot['log'][-1] 
   
			if lastOrder['side'] == "Sell":
				order = errorDetails("Sell", bot, "Ya existe actualmente una posición de venta abierta")
    
			elif lastOrder['status'] == "Open":
				order = errorDetails("Sell", bot, "Se requiere cerrar la posición de compra actual para abrir una nueva")
    
			else:
				order = createOrder("Sell", bot)
		except:
			order = createOrder("Sell", bot)


	# Cancelar ordenes
	elif request['action'] == "Close":
		try:
			lastOrder = bot['log'][-1] 
   
			if lastOrder['status'] == "Closed" or lastOrder['status'] == "Error": 
				order = errorDetails("Close", bot, "No existen posiciones por cerrar")
    
			else:
				order = closeOrder(bot)
    
		except:
			order = errorDetails(bot, "No existen posiciones por cerrar")
	
	return order, order['status']


# Función para crear operaciones
def createOrder(side, bot):
	dateTime = datetime.now(timezone(timedelta(hours=-5)))
	
	# Conecta con el exchange
	def connectExchange(bot, apiKey, apiSecret):
		global binance
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		binance.set_leverage(bot['settings']['leverage'], bot['settings']['pair'], params={"marginMode": "isolated"})
	
	# Crea las operaciones
	def binanceOrder(side, bot):
		global issues
		orderPrice = float(binance.fetch_ticker(bot['settings']['pair'])['close'])
		balance = binance.fetch_balance()['BUSD']['total']
	
		tradeAmount = ((balance * bot['settings']['leverage']) / orderPrice)

		try:
			if side == "Buy":
				order = binance.create_market_buy_order(bot['settings']['pair'], tradeAmount)
				issues = "N/A"
			elif side == "Sell":
				order = binance.create_market_sell_order(bot['settings']['pair'], tradeAmount)
				issues = "N/A"
		except:
			return errorDetails(side, bot, "Insuficiente balance para crear la orden")
   
		return order

	# Detalles de una orden
	def details(order):
		orderDetails = {
			"ID"      : order['orderID'],
			"modalID" : modalID(bot),
			"side"    : side,
			"qty"     : order['origQTY'],
			"status"  : "Open",
			"pnl"     : "",
			"open": {
				"date"    : dateTime.strftime("%d/%m/%y"),
				"time"    : dateTime.strftime("%H:%M:%S"),
				"price"   : order['price'],
				"comments": issues
				},
			"close": {
				"date"    : "",
				"time"    : "",
				"price"   : "",
				"comments": ""
				}
		}
		return orderDetails
   
	try:
		connectExchange(bot, bot['settings']['exchange']['apiKey'], bot['settings']['exchange']['apiSecret'])
		print("-- Conecta con API 1 --")
		order = binanceOrder(side, bot)
		if order['modalID'] != "":
			return order
		else:
			orderDetails = details(order)
	except:
		try:
			connectExchange(bot, bot['settings']['exchange']['apiKey2'], bot['settings']['exchange']['apiSecret2'])
			print("-- Conecta con API 2 --")
			order = binanceOrder(side, bot)
			if order['modalID'] != "":
				return order
			else:
				orderDetails = details(order)
		except:
			print("-- Error API --")
			orderDetails = errorDetails(side, bot, "No hay API valida para realizar la orden")
 
	return orderDetails


# Función para cerrar operaciones
def closeOrder(bot):
	dateTime = datetime.now(timezone(timedelta(hours=-5)))
	
	# Conecta con el exchange
	def connectExchange(apiKey, apiSecret):
		global binance
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
	
	# Crea las operaciones
	def binanceOrder(bot):
		lastOrder = bot['log'][-1]
		global issues

		try:
			if lastOrder['side'] == "Buy":
				order = binance.create_market_sell_order(bot['settings']['pair'], lastOrder['qty'], params={'reduce_only': True})
				issues = "N/A"
			elif lastOrder['side'] == "Sell":
				order = binance.create_market_buy_order(bot['settings']['pair'], lastOrder['qty'], params={'reduce_only': True})
				issues = "N/A"
		except:
			return errorDetails(lastOrder['side'], bot, "Insuficiente balance para crear la orden")
   
		return order

	# Detalles de una orden
	def details(order):
		orderDetails = {
			"ID"      : order['orderID'],
			"modalID" : modalID(bot),
			"side"    : "",
			"qty"     : order['origQTY'],
			"status"  : "Open",
			"pnl"     : "",
			"open": {
				"date"    : dateTime.strftime("%d/%m/%y"),
				"time"    : dateTime.strftime("%H:%M:%S"),
				"price"   : order['price'],
				"comments": issues
				},
			"close": {
				"date"    : dateTime.strftime("%d/%m/%y"),
				"time"    : dateTime.strftime("%H:%M:%S"),
				"price"   : order['price'],
				"comments": issues
				}
		}
		return orderDetails
   
	try:
		connectExchange(bot['settings']['exchange']['apiKey'], bot['settings']['exchange']['apiSecret'])
		order = binanceOrder(bot)
		if order['modalID'] != "":
			return order
		else:
			orderDetails = details(order)
	except:
		try:
			connectExchange(bot['settings']['exchange']['apiKey2'], bot['settings']['exchange']['apiSecret2'])
			order = binanceOrder(bot)
			if order['modalID'] != "":
				return order
			else:
				orderDetails = details(order)
		except:
			orderDetails = errorDetails("Close", bot, "No hay API valida para realizar la orden")
 
	return orderDetails


# Función para informar de errores en el bot
def errorDetails(side, bot, string):
    dateTime = datetime.now(timezone(timedelta(hours=-5)))
    orderDetails = {
			"ID"      : "XXXXXX",
			"modalID" : modalID(bot),
			"side"    : side,
			"qty"     : "",
			"status"  : "Error",
			"pnl"     : "",
			"open": {
				"date"    : dateTime.strftime("%d/%m/%y"),
				"time"    : dateTime.strftime("%H:%M:%S"),
				"price"   : "",
				"comments": string
				},
			"close": {
				"date"    : dateTime.strftime("%d/%m/%y"),
				"time"    : dateTime.strftime("%H:%M:%S"),
				"price"   : "",
				"comments": string
				}
		}
    return orderDetails

def modalID(bot):
	id = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
	for log in bot['log']: 
		if log['modalID'] == id: modalID(bot)
	return id