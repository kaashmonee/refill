from flask import Flask
from flask import Response
from flask import request
from flask import send_from_directory, send_file
import pymongo
from bson.objectid import ObjectId
import json
import datetime
import base64
import uuid
import pprint
from flask import jsonify

from bson.json_util import dumps


IP = "13.58.236.117:5000"
UPLOAD_FOLDER = 'assets'
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

    file_extension = "." in filename and filename.rsplit(".",1)[1].lower()
    if file_extension in ALLOWED_EXTENSIONS:
        return file_extension
    else:
        return None


def generate_local_image_path(location_name):
    img_file_name = str(location_name).replace(" ","")
    return UPLOAD_FOLDER + "/" + img_file_name

def generate_global_image_path(location_name):
    img_file_name = str(location_name).replace(" ","")
    return "http://" + IP + "/" + UPLOAD_FOLDER + "/" + img_file_name


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
    
     
    image_path = generate_local_image_path(name)
    with open(image_path, "wb") as fh:
        fh.write(base64.b64decode(b64image))

    global_img_path = generate_global_image_path(name)
    

    # Crafting a location object to insert into the database
    location = {
        "name": name,
        "latitude": lat,
        "longitude": long,
        "image": global_img_path, # not a 100% sure how this would work
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
    return send_file(UPLOAD_FOLDER + "/" + path, mimetype="image/jpeg", as_attachment=True)
    # return send_from_directory(UPLOAD_FOLDER, path, as_attachment=True)


if __name__ == "__main__":
    app.run()

