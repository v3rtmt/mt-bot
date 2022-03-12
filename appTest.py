from asyncio.windows_events import NULL
from flask import Blueprint, request, render_template
from Mongo.extensions import mongo


appTest = Blueprint('appTest', __name__)


@appTest.route('/addUser', methods=['POST'])
def addUser():

    user = mongo.db.Users
    user.insert_one(request.json)

    return 'User added'

@appTest.route('/addBot', methods=['POST'])
def addBot():

    bot = mongo.db.Bots
    bot.insert_one(request.json)

    return 'Bot added'

@appTest.route('/addStatus', methods=['POST'])
def addStatus():

    status = mongo.db.Status
    status.insert_one(request.json)

    return 'Status added'

# -----------------------------------------------------------------------    
    
@appTest.route('/', methods=['GET'])
def index_en():
    return render_template('EN/index_en.html')

@appTest.route('/es', methods=['GET'])
def index_es():
    return render_template('ES/index_es.html')

@appTest.route('/request', methods=['GET', 'POST'])
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

@appTest.route('/request-es', methods=['GET', 'POST'])
def request_es():

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

    return render_template('ES/requests.html')
