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
	user = mongo.db.Users.find_one({"username": session['username']})
	
	if (request.form.get("apiKey") == None) and 'username' in session:
		return render_template('Dashboard/botcreate.html', user=user, apikey=False, apiSecret=False)

	elif (request.form.get("apiKey") != None):
		
		if (request.form.get("apiKey") == ''):
			return render_template('Dashboard/botcreate.html', user=user, apiKey=True, apiSecret=False)

		if (request.form.get("apiSecret") == ''):
			return render_template('Dashboard/botcreate.html', user=user, apiKey=False, apiSecret=True)

		newBot = {
   			"ownerID"         : user['_id'],
			"ownerUser"       : user['username'],
			"isEnabled"       : True,
			"type"            : "Crypto Futures",
			"settings" : {
				"exchange" : {
					"name"        : "Binance",
					"apiKey"      : request.form.get("apiKey"),
					"apiSecret"   : request.form.get("apiSecret"),
					"apiKey2"     : request.form.get("apiKey2"),
					"apiSecret2"  : request.form.get("apiSecret2")
				},
				"pair"        : "ETH/BUSD",
				"tradeType"   : "isolated",
				"leverage"    : 50,
				"tradeAmount" : 100.00,
				"amountType"  : "USD",
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
		return redirect("/Login")


# Devuelve la pagina con informacion de un bot en especifico
@Bot.route('/Bot/<id>', methods=['GET', 'POST'])
def bot(id):
	if request.method == 'POST':
		user = mongo.db.Users.find_one({"username": session['username']})
		bot  = mongo.db.Bots.find_one({"_id": ObjectId(id)})
		
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
			mongo.db.Bots.update_one(
				{"_id": bot['_id']},
				{"$set": {"exchangeData.apiKey2": request.form.get("apiKey2"),
              			  "exchangeData.apiSecret2": request.form.get("apiSecret2")}})

  		# Elimina el Bot
		elif request.form.get("action") == "delete":
			mongo.db.Users.update_one({"_id": user['_id']}, {"$pull": {"data.bots": bot['_id']}})		
			mongo.db.Bots.delete_one({"_id": bot['_id']})
			return redirect("/Dashboard")
		
		if (bot == None) or (bot['ownerID'] != user['_id']):
			return render_template('404.html'), 404
		else:
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