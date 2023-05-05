from datetime import datetime, timedelta, timezone
import random
import string
import ccxt

def order(bot, request):
	
	# Abrir ordenes de compra
	if request['action'] == "Buy":
		for log in bot['log']:
			if log['side'] == "Buy" and log['status'] == "Open":
				order = errorDetails(bot, "Buy", "Ya existe actualmente una posición de compra abierta")
				break
			elif log['side'] == "Sell" and log['status'] == "Open":
				order = errorDetails(bot, "Buy", "Se requiere cerrar la posición de venta actual para abrir una nueva")
				break
		else: order = createOrderSimulated(bot, "Buy") if bot['isSimulated'] == True else createOrder(bot, "Buy")

	# Abrir ordenes de venta
	elif request['action'] == "Sell":
		for log in bot['log']:
			if log['side'] == "Sell" and log['status'] == "Open":
				order = errorDetails(bot, "Sell", "Ya existe actualmente una posición de venta abierta")
				break
			elif log['side'] == "Buy" and log['status'] == "Open":
				order = errorDetails(bot, "Sell", "Se requiere cerrar la posición de compra actual para abrir una nueva")
				break
		else: order = createOrderSimulated(bot, "Sell") if bot['isSimulated'] == True else createOrder(bot, "Sell")

	# Cancelar ordenes
	elif request['action'] == "Close":
		for log in bot['log']:
			if log['status'] == "Open":
				print("Si va a cancelar")
				order = closeOrderSimulated(bot, log) if bot['isSimulated'] == True else closeOrder(bot, log)
				break
		else: order = errorDetails(bot, "Close", "No existen posiciones por cerrar")
	
	return order


# Función para crear operaciones
def createOrder(bot, side):

	try:
		binance = connectExchange(bot['settings']['exchange']['apiKey'], bot['settings']['exchange']['secretKey'])
		order, balance = binanceOrder(binance)
		orderDetails = details(order, balance)
	except:
		try:
			binance = connectExchange(bot['settings']['exchange']['apiKey2'], bot['settings']['exchange']['secretKey2'])
			order, balance = binanceOrder(binance)
			orderDetails = details(binanceOrder(binance, bot, side))
		except:
			orderDetails = errorDetails(side, bot, "No hay Api key valida para realizar la orden")
	
	# Conecta con el exchange
	def connectExchange(apiKey, secretKey):
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (secretKey),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		binance.set_leverage(bot['settings']['leverage'], bot['settings']['pair'], params={"marginMode": "isolated"})
		return binance
	
	# Crea las operaciones
	def binanceOrder(binance):
		global issues
  
		balance = binance.fetch_balance()[bot['settings']['currency']]['total']
  
		if bot['settings']['amountType'] == "USD": amount = bot['settings']['orderAmount']
		elif bot['settings']['amountType'] == "%": amount = balance * (bot['settings']['orderAmount'] / 100)

		orderAmount = ((amount * bot['settings']['leverage']) / float(binance.fetch_ticker(bot['settings']['pair'])['close']))

		try:
			if   side == "Buy":  order = binance.create_market_buy_order( bot['settings']['pair'], orderAmount)
			elif side == "Sell": order = binance.create_market_sell_order(bot['settings']['pair'], orderAmount)
			print(order)
		except:
			return errorDetails(side, bot, "Insuficiente balance para crear la orden"), balance
   
		return order, balance

	# Detalles de una orden
	def details(order, balance):
		if order['modalID'] != "": return order
		else:
			try: No = bot['log'][-1]['Nº'] + 1
			except: No = 1
			dateTime = datetime.now(timezone(timedelta(hours=-5)))
			orderDetails = {
				"Nº"      : No,
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
					"balance" : balance,
					"comments": ""
					},
				"close": {
					"date"    : "",
					"time"    : "",
					"price"   : "",
					"balance" : "",
					"comments": ""
					}
			}
			return orderDetails
 
	return orderDetails


# Función para cerrar operaciones
def closeOrder(bot, position):
	
	try:
		binance = connectExchange(bot['settings']['exchange']['apiKey'], bot['settings']['exchange']['secretKey'])
		order, balance = binanceOrder(binance)
		orderDetails = details(order, balance)
	except:
		try:
			binance = connectExchange(bot['settings']['exchange']['apiKey2'], bot['settings']['exchange']['secretKey2'])
			order, balance = binanceOrder(binance)
			orderDetails = details(order, balance)
		except:
			orderDetails = errorDetails(bot, "Close", "No hay Api key valida para realizar la orden")

	# Conecta con el exchange
	def connectExchange(apiKey, apiSecret):
		binance = ccxt.binance({
			'apiKey': (apiKey),
			'secret': (apiSecret),
			'options': {'defaultType': 'future',},})
		
		binance.enableRateLimit = True
		return binance
	
	# Crea las operaciones
	def binanceOrder(binance):
		try:
			if   position['side'] == "Buy": order = binance.create_market_sell_order(bot['settings']['pair'], position['qty'], params={'reduce_only': True})
			elif position['side'] == "Sell": order = binance.create_market_buy_order(bot['settings']['pair'], position['qty'], params={'reduce_only': True})
			print(order)
			balance = binance.fetch_balance()[bot['settings']['currency']]['total']
			pnl = (balance * 100 / position['open']['balance']) - 100
		except:
			balance = binance.fetch_balance()[bot['settings']['currency']]['total']
			return errorDetails(bot, position['side'], "Error al cerrar la posición"), balance, 0
		return order, balance, pnl

	# Detalles de una orden
	def details(order, balance, pnl):
		dateTime = datetime.now(timezone(timedelta(hours=-5)))
		if order['modalID'] != "": return order
		else:
			orderDetails = {
				"Nº"      : "",
				"ID"      : "",
				"modalID" : "",
				"side"    : "",
				"qty"     : "",
				"status"  : "Closed",
				"pnl"     : pnl,
				"open": {
					"date"    : "",
					"time"    : "",
					"price"   : "",
     				"balance" : "",
					"comments": ""
					},
				"close": {
					"date"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%y"),
					"time"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%H:%M:%S"),
					"price"   : order['price'],
					"balance" : balance,
					"comments": ""
					}
			}
			return orderDetails
 
	return orderDetails


# Función para crear operaciones simuladas
def createOrderSimulated(bot, side):
	
	# Crea las operaciones
	def binanceOrder():
		
		price = float(ccxt.binance().fetch_ohlcv('BTC/USDT', '1d', limit = 1)[0][4])

		for log in reversed(bot['log']):
			if log['status'] == "Closed":
				balance = log['close']['balance']
				break
		else: balance = bot['settings']['balance']
  
		if bot['settings']['amountType'] == "USD": amount = bot['settings']['orderAmount']
		elif bot['settings']['amountType'] == "%": amount = balance * (bot['settings']['orderAmount'] / 100)

		return ((amount * bot['settings']['leverage']) / price), price, balance

	# Detalles de una orden
	def details(qty, price, balance):
		try: No = bot['log'][-1]['Nº'] + 1
		except: No = 1
		for log in reversed(bot['log']):
			if log['status'] == "Closed":
				orderID = log['ID'] + 1
				break
		else: orderID = 1
		orderDetails = {
			"Nº"      : No,
			"ID"      : orderID,
			"modalID" : modalID(bot),
			"side"    : side,
			"qty"     : qty,
			"status"  : "Open",
			"pnl"     : "",
			"open": {
				"date"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%y"),
				"time"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%H:%M:%S"),
				"price"   : price,
				"balance" : balance,
				"comments": ""
				},
			"close": {
				"date"    : "",
				"time"    : "",
				"price"   : "",
				"balance" : balance,
				"comments": ""
				}
		}
		return orderDetails

	qty, price, balance = binanceOrder()
	orderDetails = details(qty, price, balance)
 
	return orderDetails


# Función para cerrar operaciones simuladas
def closeOrderSimulated(bot, position):

	# Crea las operaciones
	def binanceOrder():
		price = float(ccxt.binance().fetch_ohlcv('BTC/USDT', '1d', limit = 1)[0][4])
  
		if position['side'] == "Buy":
			pnl = bot['settings']['leverage'] * ((price * 100 / position['open']['price']) - 100)
      
		elif position['side'] == "Sell":
			pnl = bot['settings']['leverage'] * ((position['open']['price'] * 100 / price) - 100)
   
		balance = position['open']['balance'] + (position['open']['balance'] * pnl / 100) 
		print(price)
		print(balance)
		print(pnl)
		return price, balance, pnl

	# Detalles de una orden
	def details(price, balance, pnl):
		orderDetails = {
			"Nº"      : "",
			"ID"      : "",
			"modalID" : "",
			"side"    : "",
			"qty"     : "",
			"status"  : "Closed",
			"pnl"     : pnl,
			"open": {
				"date"    : "",
				"time"    : "",
				"price"   : "",
				"balance" : "",
				"comments": ""
				},
			"close": {
				"date"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%y"),
				"time"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%H:%M:%S"),
				"price"   : price,
				"balance" : balance,
				"comments": ""
				}
		}

		return orderDetails
	
	price, balance, pnl = binanceOrder()
	orderDetails = details(price, balance, pnl)
 
	return orderDetails


# Función para informar de errores en el bot
def errorDetails(bot, side, string):
	try: No = bot['log'][-1]['Nº'] + 1 
	except: No = 1
	try: balance = bot['log'][-1]['close']['balance']
	except: balance = bot['settings']['balance']
	orderDetails = {	
			"Nº"      : No,
			"ID"      : "xxxxxx",
			"modalID" : modalID(bot),
			"side"    : side,
			"qty"     : "",
			"status"  : "Error",
			"pnl"     : "",
			"open": {
				"date"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%y"),
				"time"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%H:%M:%S"),
				"price"   : "",
				"balance" : balance,
				"comments": string
				},
			"close": {
				"date"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%d/%m/%y"),
				"time"    : datetime.now(timezone(timedelta(hours=-5))).strftime("%H:%M:%S"),
				"price"   : "",
				"balance" : balance,
				"comments": string
				}
		}

	return orderDetails


# Devuleve un ID unico para cada modal en HTML
def modalID(bot):
	id = ''.join(random.choice(string.ascii_lowercase) for i in range(20))
	for log in bot['log']: 
		if log['modalID'] == id: modalID(bot)
	return id