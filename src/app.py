"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorites
from werkzeug.security import generate_password_hash, check_password_hash
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/add_user', methods=['POST'])
def add_user():
    if request.method == 'POST':
        body = request.json
        email = body.get('email', None)
        password = body.get('password', None)

        if email is None or password is None:
            return jsonify({"message": "Password or Email needed"}, 400)
        else:
            #password = generate_password_hash(password)
            user = User(email=email, password=password, salt="123456")
            db.session.add(user)
            try:
                db.session.commit()
                return jsonify({'message': "User creates"}), 201
            except Exception as error:
                print(error.args)
                db.session.rollback()
                return jsonify({"message": error.args})

# Rutas de personas y planetas
@app.route('/people', methods=['GET'])
def get_people():
    if request.method == 'GET':
        people_query = People.query.all()
        people_list = [i.serialize() for i in people_query]
        return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id=None):
    if request.method == 'GET':
        people_query = People.query.filter_by(id=people_id).first()
        if people_query:
            person = people_query.serialize()
            return jsonify(person), 200
        else:
            return jsonify({"message":"No person found"}), 404

@app.route('/planets', methods=['GET'])
def get_planets():
    if request.method == 'GET':
        planets_query = Planet.query.all()
        planets_list = [i.serialize() for i in planets_query]
        return jsonify(planets_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id=None):
    if request.method == 'GET':
        planet_query = Planet.query.filter_by(id=planet_id).first()
        if planet_query:
            planet = planet_query.serialize()
            return jsonify(planet), 200
        else:
            return jsonify({"message":"No planet found"}), 404

# Favoritos. Estas rutas estan cableadas a un solo usuario.
# Tengo pendiente hacer dinamica esta funcion para acortarla.
@app.route('/favorite/<string:nature>/<int:nature_id>', methods=['POST', 'DELETE'])
def favorite(nature=None, nature_id=None):
    if nature == "people":
        if People.query.filter_by(id=nature_id).first():
            find_favorite = Favorites.query.filter_by(user_id=1, nature=nature, nature_id=nature_id).first()
            if not find_favorite:
                if request.method == 'POST':
                    favorite = Favorites(user_id=1, nature=nature, nature_id=nature_id)
                    db.session.add(favorite)
                    db.session.commit()
                    return jsonify({"message":"Added to favorites."}), 201
                else:
                    return jsonify({"message":"Can't delete a favorite that doesn't exist."}), 400
            else:
                if request.method == 'DELETE':
                    db.session.delete(find_favorite)
                    db.session.commit()
                    return jsonify({"message":"Favorite deleted."}), 201
                return jsonify({"message":"Favorite already exists"}), 400
        else:
            return jsonify({"message":"No person found with the id provided"}), 404
    elif nature == "planets":
        if Planet.query.filter_by(id=nature_id).first():
            find_favorite = Favorites.query.filter_by(user_id=1, nature=nature, nature_id=nature_id).first()
            if not find_favorite:
                if request.method == 'POST':
                    favorite = Favorites(user_id=1, nature=nature, nature_id=nature_id)
                    db.session.add(favorite)
                    db.session.commit()
                    return jsonify({"message":"Added to favorites."}), 201
                else:
                    return jsonify({"message":"Can't delete a favorite that doesn't exist."}), 400
            else:
                if request.method == 'DELETE':
                    db.session.delete(find_favorite)
                    db.session.commit()
                    return jsonify({"message":"Favorite deleted."}), 201
                return jsonify({"message":"Favorite already exists"}), 400
        else:
            return jsonify({"message":"No planet found with the id provided"}), 404
    else:
        return {"message":"Type of item doesn't exist in api"}, 404
    
# Rutas de usuario
@app.route('/users', methods=['GET'])
def get_users():
    if request.method == 'GET':
        users_query = User.query.all()
        users_list = [i.serialize() for i in users_query]
        return jsonify(users_list), 200

@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id=None):
    if request.method == 'GET':
        user_query = User.query.filter_by(id=user_id).first()
        user_favorites = user_query.favorites
        user_favorites = [i.serialize() for i in user_favorites]
        print(user_favorites)
        return jsonify(user_favorites), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
