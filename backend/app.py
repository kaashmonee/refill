from flask import Flask
from flask import Response
import pymongo
import json
import datetime
import base64
import uuid

from bson.json_util import dumps

UPLOAD_FOLDER = '/assets/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
mongo = pymongo.MongoClient('mongodb+srv://admin:admin@cluster0-uba4z.mongodb.net/db?retryWrites=true&w=majority', maxPoolSize=50, connect=True)


class DB: pass

db_data = DB()


@app.route("/all")
def all():
    db = pymongo.database.Database(mongo, 'db')
    col = pymongo.collection.Collection(db, 'waters') 
    cursor = col.find({})
    
    db_data.db = db
    db_data.col = col
    db_data.cursor = cursor

    return Response(dumps(col.find({})), mimetype='application/json')


def allowed_file(filename):
    """
    Determines if the file extension is one of the allowed image extensions.
    Stolen shamelessly from the flask docs
    """
    return "." in filename and filename.rsplit(".",1)[1].lower() in ALLOWED_EXTENSIONS


def generate_image_path(location_name):
    img_file_name = str(location_name) + hash(datetime.datetime.utcnow())
    return UPLOAD_FOLDER + "/" + img_file_name

@app.route("/new", methods=["POST"])
def upload_new_location():
    """
    Send a name, an image, latitude and longitude coordinates, and gross rating.
    """
    if request.method != "POST":
        raise Exception("Non POST request to POST endpoint /new")

    name = request.form["name"]
    lat = request.form["latitude"]
    long = request.form["longitude"]
    rating = request.form["gross_rating"]
    b64image = request.form["image"]
    
    with open(generate_image_path(location_name), "wb") as fh:
        fh.write(b64img.decode("base64"))
    

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
        return Response(location_id, status=200, mimetype="application/json")
    else:
        return Response("Data bad!", status=400)



def update_rating(doc_id, rating):
    loc = get_loc_object(doc_id)
    loc.gross_rating += rating
    loc.num_votes += 1


if __name__ == "__main__":
    app.run()

