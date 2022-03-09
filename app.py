from flask import Flask, request
from Mongo.extensions import mongo
from afterResponse import AfterResponse

# --- Importar Rutas de Prueba ---

from appTest import appTest

# ------------------------

# --- Importar Criptos ---

from BTC import BTC
from ETH import ETH

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
	app.register_blueprint(appTest)

	# -- Ejecuta Criptos --
	app.register_blueprint(BTC)
	app.register_blueprint(ETH)

	# -- Inicia aplicacion --
	return app
 