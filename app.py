from flask import Flask
from Mongo.extensions import mongo
from afterResponse import AfterResponse
from datetime import timedelta

# --- Importar Rutas de Prueba ---

from appRoutes import appRoutes, profile

# ------------------------

# --- Importar Criptos ---

from BTC import BTC
from ETH import ETH
from BNB import BNB
from SOL import SOL

# ------------------------


def create_app(config_object='Mongo.settings'):

	# -- Crea aplicacion --
	app = Flask(__name__)

	# -- Configura aplicacion --
	app.config['MONGO_URI'] = 'mongodb+srv://vert:V3rtcontra$ena@mtstrategy.3zpyn.mongodb.net/MTStrategy?retryWrites=true&w=majority'
	AfterResponse(app)

	# -- Inicia Base de Datos --
	mongo.init_app(app)

	# -- Ejecuta Rutas de Prueba --
	app.register_blueprint(appRoutes)

	# -- Configuracion de cookies --
	app.secret_key = "mtstrategy"
	app.permanent_session_lifetime = timedelta(days=8)

	# -- Ejecuta Criptos --
	app.register_blueprint(BTC)
	app.register_blueprint(ETH)
	app.register_blueprint(BNB)
	app.register_blueprint(SOL)
	
	# -- Carpeta temporal fotos de perfil --
	profilePics = 'static/profilePics/'
	app.config['UPLOAD_FOLDER'] = profilePics

	# -- Inicia aplicacion --
	return app

app = create_app()
