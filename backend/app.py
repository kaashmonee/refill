from flask import Flask
import pymongo
import json

from bson.json_util import dumps

app = Flask(__name__)

mongo = pymongo.MongoClient('mongodb+srv://admin:admin@cluster0-uba4z.mongodb.net/db?retryWrites=true&w=majority', maxPoolSize=50, connect=True)

@app.route("/")
def hello():
    return "shawn is exceedingly gay!"


@app.route("/testdb")
def test_db():
    db = pymongo.database.Database(mongo, 'db')
    col = pymongo.collection.Collection(db, 'waters') 
    cursor = col.find({})
    return dumps(col.find({}))

if __name__ == "__main__":
    app.run()

