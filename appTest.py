from flask import Blueprint, request
from bson.objectid import ObjectId
import time
import ccxt
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