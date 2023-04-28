from Mongo.extensions import mongo
from flask			  import Blueprint, redirect, render_template, request, current_app as app, session
from bson             import ObjectId
import Binance


# --------------

Bot = Blueprint('Bot', __name__)

# --------------

# Devuelve la pagina para crear un nuevo bot
@Bot.route('/Bot/create', methods=['GET', 'POST'])
def createbot():
	print(request.form)
	user = mongo.db.Users.find_one({"username": session['username']})
 
	if request.method == 'POST':
		
		if (request.form.get("apiKey") == ''):
			return render_template('Dashboard/botcreate.html', user=user, apiKey=True, apiSecret=False)

		if (request.form.get("SecretKey") == ''):
			return render_template('Dashboard/botcreate.html', user=user, apiKey=False, apiSecret=True)

		if (float(request.form.get("orderAmount")) > 100) and (request.form.get("amountType") == "%"): orderAmount = 100
		elif (float(request.form.get("orderAmount")) < 0) and (request.form.get("amountType") == "%"): orderAmount = 0
		else: orderAmount = float(request.form.get("orderAmount"))
		
		if int(request.form.get("leverage")) > 100: leverage = 100
		elif int(request.form.get("leverage")) < 1: leverage = 1
		else: leverage = int(request.form.get("leverage"))
  
		isSimulated = True if request.form.get("isSimulated") else False
  
		newBot = {
   			"ownerID"         : user['_id'],
			"ownerUser"       : user['username'],
			"type"            : "Crypto Futures",
			"isEnabled"       : True,
			"isSimulated"     : isSimulated,
			"settings" : {
				"exchange" : {
					"name"        : request.form.get("exchange"),
					"apiKey"      : request.form.get("apiKey"),
					"secretKey"   : request.form.get("secretKey"),
					"apiKey2"     : request.form.get("apiKey2"),
					"secretKey2"  : request.form.get("secretKey2")
				},
				"pair"        : request.form.get("pair"),
				"tradeType"   : "isolated",
				"orderAmount" : orderAmount,
				"amountType"  : request.form.get("amountType"),
				"leverage"    : leverage,
				"notifications" : {
					"emailNotifications"    : False,
					"emailEntry"            : False,
					"emailClose"            : False,
					"telegramNotifications" : False,
					"telegramEntry"         : False,
					"telegramClose"         : False,
				},
			},
			"log": []
   		}
		
		botID = mongo.db.Bots.insert_one(newBot).inserted_id
		mongo.db.Users.update_one({"_id": user['_id']}, {"$push": {"data.bots": botID}})

		return redirect(f"/Bot/{botID}")
		
	else:
		if 'username' in session:
			return render_template('Dashboard/botcreate.html', user=user, apikey=False, apiSecret=False)
		else:
			return redirect("/Login")


# Devuelve la pagina con informacion de un bot en especifico
@Bot.route('/Bot/<id>', methods=['GET', 'POST'])
def bot(id):
	if request.method == 'POST':
		user = mongo.db.Users.find_one({"username": session['username']})
		bot  = mongo.db.Bots.find_one({"_id": ObjectId(id)})
		print("aqui empieza")
  
  		# Activa el Bot
		if request.form.get("action") == "active":
			mongo.db.Bots.update_one(
				{"_id": bot['_id']},
				{"$set": {"isEnabled": True}})
   
     	# Desactiva el Bot
		elif request.form.get("action") == "inactive":
			mongo.db.Bots.update_one(
				{"_id": bot['_id']},
				{"$set": {"isEnabled": False}})

  		# Actualiza el Bot
		elif request.form.get("action") == "update":
			if (float(request.form.get("orderAmount")) > 100) and (request.form.get("amountType") == "%"): orderAmount = 100
			elif (float(request.form.get("orderAmount")) < 0) and (request.form.get("amountType") == "%"): orderAmount = 0
			else: orderAmount = float(request.form.get("orderAmount"))
			
			if int(request.form.get("leverage")) > 100: leverage = 100
			elif int(request.form.get("leverage")) < 1: leverage = 1
			else: leverage = int(request.form.get("leverage"))
   
			mongo.db.Bots.update_one(
				{"_id": bot['_id']},
				{"$set": {"settings.exchange.apiKey2": request.form.get("apiKey2"),
              			  "settings.exchange.secretKey2": request.form.get("secretKey2"),
                   		  "settings.orderAmount": orderAmount,
                          "settings.amountType": request.form.get("amountType"),
                          "settings.leverage": leverage}})

  		# Elimina el Bot
		elif request.form.get("action") == "delete":
			mongo.db.Users.update_one({"_id": user['_id']}, {"$pull": {"data.bots": bot['_id']}})		
			mongo.db.Bots.delete_one({"_id": bot['_id']})
			return redirect("/Dashboard")
		
		if (bot == None) or (bot['ownerID'] != user['_id']):
			return render_template('404.html'), 404
		else:
			print("aqui termina")
			return redirect(f'/Bot/{id}')

	else:
		if 'username' in session:
			user = mongo.db.Users.find_one({"username": session['username']})
			bot  = mongo.db.Bots.find_one({"_id": ObjectId(id)})
			if (bot == None) or (bot['ownerID'] != user['_id']):
				return render_template('404.html'), 404
			else:
				return render_template('Dashboard/bot.html', user=user, bot=bot)
		else:
			return redirect("/Login")


# Ruta para hacer operaciones con un bot    
@Bot.route('/Bot/post/<identifier>', methods=['POST'])
def afterBotPost(identifier):
	global id 
	global reqJson
	id = identifier
 
	if request.form.get("action") == "Buy":
		reqJson = {"action": "Buy"}

	elif request.form.get("action") == "Sell":
		reqJson = {"action": "Sell"}

	elif request.form.get("action") == "Close":
		reqJson = {"action": "Close"}

	else:
		reqJson = request.json

	@app.after_response
	def BotPost():
		bot = mongo.db.Bots.find_one({"_id": ObjectId(id)})
		
		# Crypto Futures
		if bot['type'] == "Crypto Futures":
			if bot['settings']['exchange']['name'] == "Binance":
				order, type = Binance.order(bot, reqJson)
			if bot['settings']['exchange']['name'] == "Bybit":
				pass # order = Bybit.order(bot, req)
		
		if type == "Open" or type == "Error":
			mongo.db.Bots.update_one({"_id": bot['_id']}, {"$push": {"log": order}})
		else:
			mongo.db.Bots.update_one(
				{"_id": bot['_id'], "log.status": "Open"},
				{"$set": {
					"Log.$.status"        : "Closed",
					"Log.$.pnl"           : order['pnl'],
					"Log.$.close.date"    : order['close']['date'],
					"Log.$.close.time"    : order['close']['time'],
					"Log.$.close.price"   : order['close']['price'],
					"Log.$.close.comments": order['close']['comments']
					}
				}
			)
	
	if not request.form.get("action"):
		return '200'
	else:
		return redirect(f'/Bot/{id}')