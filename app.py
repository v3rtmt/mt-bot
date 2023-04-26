from flask            import Flask, render_template
from Mongo.extensions import mongo
from afterResponse    import AfterResponse
from datetime         import timedelta

# --- Importar Rutas de App ---

from Routes import Routes
from Bot    import Bot

def create_app(config_object='Mongo.settings'):

	# -- Crea aplicacion --
	app = Flask(__name__)

	# -- Configura aplicacion --
	app.config['MONGO_URI'] = 'mongodb+srv://vert:V3rtcontra$ena@mtstrategy.3zpyn.mongodb.net/MTStrategy?retryWrites=true&w=majority'
	AfterResponse(app)

	# -- Inicia Base de Datos --
	mongo.init_app(app)

	# -- Ejecuta Rutas de Prueba --
	app.register_blueprint(Routes)
	app.register_blueprint(Bot)

	# -- Configuracion de cookies --
	app.secret_key = "mtstrategy"
	app.permanent_session_lifetime = timedelta(days=8)
	
	# -- Carpeta temporal fotos de perfil --
	profilePics = 'static/profilePics/'
	app.config['UPLOAD_FOLDER'] = profilePics

	# -- Error 404 --
	@app.errorhandler(404)
	def page_not_found(error):
		return render_template('404.html'), 404
    
	# -- Inicia aplicacion --
	return app

app = create_app()