from flask import Flask
from flask import Response
from flask import request
import pymongo
import json
import datetime
import base64
import uuid
import pprint

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
    
    if location:
        # successful
        return Response(str(location_id), status=200, mimetype="application/json")
    else:
        return Response("Data bad!", status=400)


@app.route("/get_by_name", methods=["GET"])
def return_resource_by_name():
    """
    This function returns the resource specified by the name in the get request.
    """
    pass


@app.route("/get_uid", methods=["GET"])
def return_uid_resource():
    """
    This endpoint should return the resource with the specified UID. 
    """
    pass


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




if __name__ == "__main__":
    app.run()

