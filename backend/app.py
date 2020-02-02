from flask import Flask
from flask import Response
from flask import request
import pymongo
from bson.objectid import ObjectId
import json
import datetime
import base64
import uuid
import pprint
from flask import jsonify

from bson.json_util import dumps


UPLOAD_FOLDER = './assets'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = pymongo.MongoClient('mongodb+srv://admin:admin@cluster0-uba4z.mongodb.net/db?retryWrites=true&w=majority', maxPoolSize=50, connect=True)


class DB: 
    def __init__(self):
        self.db = pymongo.database.Database(mongo, 'db')
        self.col = pymongo.collection.Collection(self.db, 'waters') 
        self.cursor = self.col.find({})
        
db_data = DB()

@app.route("/all")
def all():
    
    response = Response(dumps(db_data.col.find({})), mimetype='application/json')
    response.headers.add("Access-Control-Allow-Origin", "*")

    return response 


def allowed_file(filename):
    """
    Determines if the file extension is one of the allowed image extensions.
    Stolen shamelessly from the flask docs
    """
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


def generate_image_path(location_name):
    img_file_name = str(location_name) + str(hash(datetime.datetime.utcnow()))
    return UPLOAD_FOLDER + "/" + img_file_name


@app.route("/new", methods=["POST"])
def upload_new_location():
    """
    Send a name, an image, latitude and longitude coordinates, and gross rating.
    """
    if request.method != "POST":
        raise Exception("Non POST request to POST endpoint /new")
    

    name = request.json["name"]
    lat = request.json["latitude"]
    long = request.json["longitude"]
    rating = request.json["gross_rating"]
    b64image = request.json["image"]
    
     
    image_path = generate_image_path(name)
    with open(image_path, "wb") as fh:
        fh.write(base64.b64decode(b64image))
    

    # Crafting a location object to insert into the database
    location = {
        "name": name,
        "latitude": lat,
        "longitude": long,
        "image": image_path, # not a 100% sure how this would work
        "gross_rating": rating,
        "num_votes": 1,
        "last_updated": datetime.datetime.utcnow()
    }

    locations = db_data.col # returns the water collection
    location_id = locations.insert_one(location).inserted_id
    
    response = ""
    if location:
        # successful
        response = Response(str(location_id), status=200, mimetype="application/json")
    else:
        response = Response("Data bad!", status=400)
    
    print(str(location_id))
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


def get_response_from_collection_find(cursor):
    cursor_dump = dumps(cursor)
    print("cursor dump:", cursor_dump)
    response = Response(cursor_dump, status=200, mimetype="application/json")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route("/get_by_name")
def return_resource_by_name():
    """
    This function returns the resource specified by the name in the get request.
    """
    name = request.args.get("name")
    cursor = db_data.col.find({"name": name})

    return get_response_from_collection_find(cursor)


@app.route("/get_by_uid", methods=["GET"])
def return_uid_resource():
    # Do not use this. it basically doesn't work
    uid = request.args.get("uid")
    cursor = db_data.col.find({u'_id': ObjectId(uid)})

    print(dumps(cursor))

    # For some reason, the response is empty, and I have no idea why.
    return get_response_from_collection_find(cursor)


@app.route("/update_rating", methods=["POST"])
def update_rating():
    """
    This function simply updates the gross rating of the location.
    """
    name = request.json["name"]
    gross_rating = request.json["gross_rating"]

    result = db_data.col.update_one(
        {"name": name}, 
        {
            "$set": {"gross_rating": gross_rating},
            "$inc": {"num_votes": 1}
        }, 
        upsert=False
    )
    
    # Testing code to make sure this endpoint works.
    # cursor = db_data.col.find({"name": name})
    # for doc in cursor:
    #    pprint.pprint(doc)

    return Response(str(result), status=200, mimetype="application/json")

@app.route("/assets/<path:path>")
def send_image(path):
    ip = "http://13.58.236.117:5000/home/refill/backend"
    full_path = ip + path
    return send_from_directory(full_path)

@app.route("/query", methods=["GET"])
def get_neighboring_fountains():
    """
    Given clients's position, get info of neighboring fountains
    """
    if request.method != "GET":
        raise Exception("Non GET request to GET endpoint /query")
    
    req = request.query_string
    clat,clong = req.decode('utf-8').split('&')
    clat = float(clat.split('=')[1])
    clong = float(clong.split('=')[1])
    cutoff = 10

    # print(clat,clong)
    # sorting the database by proximity to the client
    locs = db_data.col.find()
    locs = list(locs)

    dists = [(clat-loc['latitude'])**2+(clong-loc['longitude'])**2 for loc in locs]
    dists = list(enumerate(dists))
    dists.sort(key=lambda x:x[1])
    payload = [locs[ind] for ind,_ in dists[:cutoff]]

    return Response(str(payload), status=200, mimetype="application/json")


if __name__ == "__main__":
    app.run()

