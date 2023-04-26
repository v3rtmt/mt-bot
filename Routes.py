from apscheduler.schedulers.background import BackgroundScheduler
from Mongo.extensions                  import mongo
from datetime                          import datetime, timedelta, timezone
from flask				               import Blueprint, redirect, render_template, request, session
import base64
import atexit
import ccxt


# En este Blueprint se registran las rutas que sirven para desplegar la mayoria de la aplicacion
# -------------------------------------
Routes = Blueprint('Routes', __name__)
# -------------------------------------


# Devuleve página de informacion de la aplicación
@Routes.route('/', methods=['GET'])
def index():
	return render_template('index.html')


# Devuelve página de inicio de sesión
@Routes.route('/Login', methods=['GET', 'POST'])
def login():

	# Devuelve a /Dashboard si hay token de sesión guardado
	if (request.form.get("username") == None) and ('username' in session):
		return redirect("/Dashboard")

	# Proceso de inicio de sesión
	elif (request.form.get("username") != None):
		user = mongo.db.Users.find_one({"username": request.form.get("username")})
  
		# Verifica los datos de inicio de sesión
		if user == None:
			return render_template('login.html', usernameError=True, passwordError=False, username=request.form.get("username"))
		elif user['data']['credentials']['password'] != request.form.get("password"):	
			return render_template('login.html', usernameError=False, passwordError=True, username=request.form.get("username"))

		# Guarda token de inicio de sesión
		if request.form.get("remember") == "true":
			session.permanent = True
			session['username'] = request.form.get("username")
		else:
			session.permanent = False
			session['username'] = request.form.get("username")
   
		return redirect("/Dashboard")

	return render_template('login.html', usernameError=False, passwordError=False, username="")


# Cierra sesión y devuelve página de inicio de sesión
@Routes.route('/Logout', methods=['GET'])
def logout():
	session.pop('username', None)
	return redirect("/Login")


# Devuelve página de registro de nuevo usuario
@Routes.route('/Register', methods=['GET', 'POST'])
def register():

	# Devuelve a /Dashboard si hay token de sesión guardado
	if (request.form.get("name") == None) and ('username' in session):
		return redirect("/Dashboard")

	# Proceso de registro de usuario
	elif (request.form.get("name") != None):
	 
		# Devuelve si el username ya esta registrado
		if mongo.db.Users.find_one({"username": request.form.get("username")}):
			return render_template('register.html', emailError=False, usernameError=True, usercode=False, name=request.form.get("name"), username=request.form.get("username"), email=request.form.get("email"))

		# Devuelve si el email ya esta registrado
		if mongo.db.Users.find_one({"data.credentials.email": request.form.get("email")}):
			return render_template('register.html', emailError=True, usernameError=False, usercode=False, name=request.form.get("name"), username=request.form.get("username"), email=request.form.get("email"))
		
		# Devuelve si no cuenta con codigo de acceso
		if str(mongo.db.Data.find_one({"data": True})['usercode']) != str(request.form.get("usercode")):
			return render_template('register.html', emailError=False, usernameError=False, usercode=True, name=request.form.get("name"), username=request.form.get("username"), email=request.form.get("email"))

		dateTime = datetime.now(timezone(timedelta(hours=-5)))

		# Datos nuevo usuario
		newUser = {
			"username": request.form.get("username"),
			"name"    : request.form.get("name"),
			"range"   : "Usuario",
			"profilePicture": {
				"img64": mongo.db.Data.find_one({"data": True})['defaultPicture']['img64']
			},
			"data": {
				"credentials": {
					"email"   : request.form.get("email"),
					"telegram": "",
					"password": request.form.get("password")
				},
				"details": {
					"registerDay" : dateTime.strftime("%d/%m/%y"),
					"registerTime": dateTime.strftime("%H:%M:%S"),
				},
				"notifications": {
					"emailNotifications"   : False,
					"emailEntry"           : False,
					"emailClose"           : False,
					"telegramNotifications": False,
					"telegramEntry"        : False,
					"telegramClose"        : False,
				},
				"bots": []
			}
		}

		# Registra nuevo usuario
		mongo.db.Users.insert_one(newUser)
		return redirect("/Login")

	return render_template('register.html', emailError=False, usernameError=False, name="", username="", email="")


# Devuelve la página del panel de control de la cuenta
@Routes.route('/Dashboard', methods=['GET'])
def dashboard():
	if 'username' in session:
		user = mongo.db.Users.find_one({"username": session['username']})
		data = mongo.db.Data.find_one({"data": True})
		return render_template('Dashboard/dashboard.html', user=user, data=data)
	else:
		return redirect("/Login")


# Devuelve la página de notificaciones de la cuenta
@Routes.route('/Notifications', methods=['GET'])
def notifications():
	if 'username' in session:
		user = mongo.db.Users.find_one({"username": session['username']})
		return render_template('Dashboard/notifications.html', user=user)
	else:
		return redirect("/Login")


# Devuelve la página con la informacion del usuario
@Routes.route('/Profile', methods=['GET', 'POST'])
def profile():
	if 'username' in session:
		user = mongo.db.Users.find_one({"username": session['username']})

		# Devuelve página con información
		if request.method == 'GET':
			return render_template('Dashboard/profile.html', user=user)

		# Edita perfil del usuario
		elif request.method == 'POST':

			# Atualiza imagen del usuario
			image = request.files['profilePicture']
			img64 = str(base64.b64encode(image.read()))[2:][:-1]
			if (image.filename != "") and (img64 != user['profilePicture']['img64']):
				mongo.db.Users.update_one(
					{"username": user['username']},
					{"$set": {"profilePicture.img64": str(img64)}})
			
			# Actualiza nombre del usuario
			if user['name'] != request.form.get("name"):
				mongo.db.Users.update_one(
					{"username": user['username']},
					{"$set": {"name": str(request.form.get("name"))}})

			# Actualiza correo del usuario
			if user['data']['credentials']['email'] != request.form.get("email"):
				if mongo.db.Users.find_one({"data.credentials.email": request.form.get("email")}):
					return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=True, telegramError=False)
				else:
					mongo.db.Users.update_one(
						{"username": user['username']},
						{"$set": {"data.credentials.email": str(request.form.get("email"))}})

			# Actualiza telegram del usuario
			if user['data']['credentials']['telegram'] != request.form.get("telegram"):
				if mongo.db.Users.find_one({"data.credentials.telegram": request.form.get("telegram")}):
					return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=False, telegramError=True)
				else:
					mongo.db.Users.update_one(
						{"username": user['username']},
						{"$set": {"data.credentials.telegram": str(request.form.get("telegram"))}})
			
			return redirect("/Profile")
	else:
		return redirect("/Login")


# Ruta para editar informacion del usuario
@Routes.route('/Profile/edit', methods=['POST'])
def profileEdit():

	if 'username' in session:
		user = mongo.db.Users.find_one({"username": session['username']})

		# Atualiza imagen del usuario
		image = request.files['profilePicture']
		img64 = str(base64.b64encode(image.read()))[2:][:-1]
		if (image.filename != "") and (img64 != user['profilePicture']['img64']):
			mongo.db.Users.update_one(
				{"username": user['username']},
				{"$set": {"profilePicture.img64": str(img64)}})
		
		# Actualiza nombre del usuario
		if user['name'] != request.form.get("name"):
			mongo.db.Users.update_one(
				{"username": user['username']},
				{"$set": {"name": str(request.form.get("name"))}})

		# Actualiza correo del usuario
		if user['data']['credentials']['email'] != request.form.get("email"):
			if mongo.db.Users.find_one({"data.credentials.email": request.form.get("email")}):
				return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=True, telegramError=False)
			else:
				mongo.db.Users.update_one(
					{"username": user['username']},
					{"$set": {"data.credentials.email": str(request.form.get("email"))}})

		# Actualiza telegram del usuario
		if user['data']['credentials']['telegram'] != request.form.get("telegram"):
			if mongo.db.Users.find_one({"data.credentials.telegram": request.form.get("telegram")}):
				return render_template('Dashboard/profile.html', user=user, imageError=False, emailError=False, telegramError=True)
			else:
				mongo.db.Users.update_one(
					{"username": user['username']},
					{"$set": {"data.credentials.telegram": str(request.form.get("telegram"))}})
		 
		return redirect("/Profile")
	else:
		return redirect("/Login")


# Devuelve la página de ayuda al usuario
@Routes.route('/Help', methods=['GET'])
def help():
	if 'username' in session:
		user = mongo.db.Users.find_one({"username": session['username']})
		return render_template('Dashboard/help.html', user=user)
	else:
		return redirect("/Login")


# Actualiza los precios de las monedas en la base de datos cada 30 segundos
def prices(): 
	binance = ccxt.binance()
	btc = binance.fetch_ohlcv('BTC/USDT', '1d', limit = 1)
	eth = binance.fetch_ohlcv('ETH/USDT', '1d', limit = 1)

	mongo.db.Data.update_one(
		{"data": True},
		{"$set": 
	  		{"btcPrice" : btc[0][4],  
			 "ethPrice" : eth[0][4], 
			 "btcChange": ((btc[0][4]) * 100 / (btc[0][1])) - 100,
			 "ethChange": ((eth[0][4]) * 100 / (eth[0][1])) - 100}})

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(prices, 'interval', seconds=30)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())