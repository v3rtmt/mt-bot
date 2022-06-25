from flask import Blueprint, jsonify, redirect, render_template, request, current_app as app, session
from Mongo.extensions import mongo
from scheduler import Scheduler
import time
import ccxt
import datetime
import pytz
import base64

from BTC import scheduleBTC
#from ETH import scheduleETH

# RECORDATORIO DE ORDENAR T0D0 ESTE JALE


appRoutes = Blueprint('appRoutes', __name__)

# -----------------------------------------------------------------------
#								FRONTEND
# -----------------------------------------------------------------------

@appRoutes.route('/', methods=['GET'])
def index_en():
	return render_template('index.html')

@appRoutes.route('/Login', methods=['GET', 'POST'])
def login():

	if request.form.get("username") == None:
		if 'username' in session:
			return redirect("/Dashboard")
	else:
		mongoUser = mongo.db.newUser

		usernameFilter = {"username": request.form.get("username")}

		user = mongoUser.find_one(usernameFilter)
		if user == None:
			return render_template('login.html', usernameError=True, passwordError=False, username=request.form.get("username"))

		elif user['data']['credentials']['password'] != request.form.get("password"):	
			return render_template('login.html', usernameError=False, passwordError=True, username=request.form.get("username"))

		if request.form.get("remember") == "true":
			session.permanent = True
			session['username'] = request.form.get("username")
		else:
			session.permanent = False
			session['username'] = request.form.get("username")

		return redirect("/Dashboard")

	return render_template('login.html', usernameError=False, passwordError=False, username="")

@appRoutes.route('/Register', methods=['GET', 'POST'])
def register():

	if request.form.get("name") == None:
		if 'username' in session:
			return redirect("/Dashboard")
	else:
		mongoUser = mongo.db.newUser

		emailFilter = {"user.credentials.email": request.form.get("email")}
		usernameFilter = {"username": request.form.get("username")}
		emailfound = mongoUser.find_one(emailFilter)
		usernamefound = mongoUser.find_one(usernameFilter)

		if mongoUser.find_one(emailFilter):
			print(emailfound)
			return render_template('register.html', emailError=True, usernameError=False, name=request.form.get("name"), username=request.form.get("username"), email=request.form.get("email"))

		if mongoUser.find_one(usernameFilter):
			print(usernamefound)
			return render_template('register.html', emailError=False, usernameError=True, name=request.form.get("name"), username=request.form.get("username"), email=request.form.get("email"))
		

		name = request.form.get("name")
		username = request.form.get("username")
		email = request.form.get("email")
		password = request.form.get("password")

		dateTimeUTC = datetime.datetime.now(tz=pytz.UTC)
		dateTime = dateTimeUTC.astimezone(pytz.timezone('America/Monterrey'))
		date = dateTime.strftime("%d/%m/%y")
		ctime = dateTime.strftime("%H:%M:%S")

		img = mongoUser.find_one({"deft": True})
		img64 = img['defaultPic']['img64']
		
		newUser = {
			"username": username,
			"name": name,
			"range": "Usuario",
			"commission": 20,
			"profilePicture": {
				"img64": img64
			},
			"data": {
				"credentials": {
					"email": email,
					"telegram": "",
					"password": password
				},
				"details": {
					"registerDay": date,
					"registerTime": ctime,
					"generalCommissionCharge": 20
				},
				"notifications": {
					"emailNotifications": True,
					"emailChanges": True,
					"emailRegister": False,
					"emailCommissions": False,
					"telegramNotifications": False,
					"telegramChanges": False,
					"telegramRegister": False,
					"telegramCommissions": False
				},
				"bots": []
			}
		}

		mongoUser.insert_one(newUser)

		return redirect("/Login")

	return render_template('register.html', emailError=False, usernameError=False, name="", username="", email="")

@appRoutes.route('/Logout', methods=['GET', 'POST'])
def logout():
	session.pop('username', None)
	return redirect("/Login")

@appRoutes.route('/Dashboard', methods=['GET'])
def dashboard():
	if 'username' in session:
		mongoUser = mongo.db.newUser
		user = mongoUser.find_one({"username": session['username']})
		return render_template('Dashboard/dashboard.html', user=user)
	else:
		return redirect("/Login")

@appRoutes.route('/Notifications', methods=['GET'])
def notifications():
	if 'username' in session:
		mongoUser = mongo.db.newUser
		user = mongoUser.find_one({"username": session['username']})
		return render_template('Dashboard/notifications.html', user=user)
	else:
		return redirect("/Login")

@appRoutes.route('/Bots', methods=['GET'])
def bots():
	return render_template('Dashboard/bots.html') # --- 404 ---

@appRoutes.route('/Profile', methods=['GET'])
def profile():
	if 'username' in session:
		mongoUser = mongo.db.newUser
		user = mongoUser.find_one({"username": session['username']})
		return render_template('Dashboard/profile.html', user=user)
	else:
		return redirect("/Login")

@appRoutes.route('/Profile/edit', methods=['POST'])
def profileEdit():
	
	if 'username' in session:

		mongoUser = mongo.db.newUser
		usernameFilter = {"username": session['username']}
		user = mongoUser.find_one(usernameFilter)

		image = request.files['profilePicture']
		
		if image.filename != "":
			print("Image edit")
			image_read = image.read()
			image_64_encode = base64.b64encode(image_read)
			str64 = str(image_64_encode)
			img64 = str64[2:][:-1]

			if img64 != user['profilePicture']['img64']:
				mongoUser.update_one(
					{"username": user['username']},
					{"$set": {"profilePicture.img64": str(img64)}}
				)
		
		if user['name'] != request.form.get("name"):
			mongoUser.update_one(
				{"username": user['username']},
				{"$set": {"name": str(request.form.get("name"))}}
			)

		if user['data']['credentials']['email'] != request.form.get("email"):
			emailFilter = {"data.credentials.email": request.form.get("email")}

			if mongoUser.find_one(emailFilter):
				return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=True, telegramError=False)

			mongoUser.update_one(
				{"username": user['username']},
				{"$set": {"data.credentials.telegram": str(request.form.get("email"))}}
			)

		if user['data']['credentials']['telegram'] != request.form.get("telegram"):
			teleFilter = {"data.credentials.telegram": request.form.get("telegram")}

			if mongoUser.find_one(teleFilter):
				return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=False, telegramError=True)

			mongoUser.update_one(
				{"username": user['username']},
				{"$set": {"data.credentials.telegram": str(request.form.get("telegram"))}}
			)
		 
		return redirect("/Profile")
	else:
		return redirect("/Login")

@appRoutes.route('/Help', methods=['GET'])
def help():
	if 'username' in session:
		mongoUser = mongo.db.newUser
		user = mongoUser.find_one({"username": session['username']})
		return render_template('Dashboard/help.html', user=user)
	else:
		return redirect("/Login")



# -----------------------------------------------------------------------
#								BACKTEND
# -----------------------------------------------------------------------

@appRoutes.route('/Schedule', methods=['POST'])
def scheduler():
	print(scheduleBTC)
	#print(scheduleETH)
	@app.after_response
	def init():
		while True:
			scheduleBTC.exec_jobs()
			#scheduleETH.exec_jobs()
			time.sleep(3)
	return 'Scheduel'

@appRoutes.route('/addUser', methods=['POST'])
def addUser():
	user = mongo.db.Users
	user.insert_one(request.json)
	return 'User added'

@appRoutes.route('/addBot', methods=['POST'])
def addBot():
	bot = mongo.db.Bots
	bot.insert_one(request.json)
	return 'Bot added'

@appRoutes.route('/addStatus', methods=['POST'])
def addStatus():
	status = mongo.db.Status
	status.insert_one(request.json)
	return 'Status added'

@appRoutes.route('/request', methods=['GET', 'POST'])
def request_en():

	if request.form.get("name") == None:
		pass
	else:
		name = request.form.get("name")
		lastName = request.form.get("lastName")
		email = request.form.get("email")
		type = request.form.get("type")
		description = request.form.get("description")

		newRequest = {
			"Name": name,
			"Last Name": lastName,
			"Email": email,
			"Type": type,
			"Description": description 
		}
		setRequest = mongo.db.Request
		setRequest.insert_one(newRequest)

	return render_template('EN/requests.html')

@appRoutes.route('/test', methods=['GET', 'POST'])
def test():
	@app.after_response
	def cre():
		import time
		binance = ccxt.binance({
				'apiKey': 'hJkAG2ynUNlMRGn62ihJh5UgKpZKk6U2wu0BXmKTvlZ5VBATNd1SRdAN43q9Jtaq',
				'secret': '3b7qmlRibSsbnLQhHIoOFogqROqr9FXxg563nyRj5pjJsvcJWpFnxyggA5TaTyfJ',
				'options': {
					'defaultType': 'future',
				},
			})
		binance.set_leverage(50, 'BTC/BUSD', params={"marginMode": "isolated"})
		#datetime_object = datetime.datetime.now()
		#tickerBUSD = binance.fetch_ticker('BTC/BUSD')
		#priceBUSD = float(tickerBUSD['close'])
		tradeAmount = 0.001
		clock = [
		"450", "451", "452", "453", "454", "455", "456", "457", "458", "459",
		"950", "951", "952", "953", "954", "955", "956", "957", "958", "959",
		"1450", "1451", "1452", "1453", "1454", "1455", "1456", "1457", "1458", "1459",  
		"1950", "1951", "1952", "1953", "1954", "1955", "1956", "1957", "1958", "1959",  
		"2450", "2451", "2452", "2453", "2454", "2455", "2456", "2457", "2458", "2459",  
		"2950", "2951", "2952", "2953", "2954", "2955", "2956", "2957", "2958", "2959",  
		"3450", "3451", "3452", "3453", "3454", "3455", "3456", "3457", "3458", "3459",  
		"3950", "3951", "3952", "3953", "3954", "3955", "3956", "3957", "3958", "3959",  
		"4450", "4451", "4452", "4453", "4454", "4455", "4456", "4457", "4458", "4459",  
		"4950", "4951", "4952", "4953", "4954", "4955", "4956", "4957", "4958", "4959",  
		"5450", "5451", "5452", "5453", "5454", "5455", "5456", "5457", "5458", "5459",  
		"5950", "5951", "5952", "5953", "5954", "5955", "5956", "5957", "5958", "5959"  
		]
		
		def create():
			import time
			orderTime1 = time.localtime()
			orderTime = str(orderTime1.tm_min) + str(orderTime1.tm_sec)

			if orderTime in clock:
				order = binance.create_market_sell_order('BTC/BUSD', tradeAmount)
				print(order['datetime'])
				print(order['price'])

				time.sleep(3)

				order = binance.create_market_buy_order('BTC/BUSD', tradeAmount, params={'reduce_only': True})	
				print(order['datetime'])
				print(order['price'])
			else:
				time.sleep(1.1)
				create()

		create()

	return 'did'