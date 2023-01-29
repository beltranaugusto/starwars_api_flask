from flask_sqlalchemy import SQLAlchemy
from enum import Enum

db = SQLAlchemy()

class Nature(Enum):
    planets = "Planets"
    people = "People"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    description = db.Column(db.String(300), unique=False, nullable=True)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship('Favorites', backref='user', lazy=True)
    

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nature_id = db.Column(db.Integer, unique=False, nullable=False)
    nature = db.Column(db.Enum(Nature), nullable=False)

    def __repr__(self):
        return f'<Favorites {self.nature}: {self.nature_id}>'
    
    def serialize(self):
        return {
            "user_id": self.user_id,
            "nature": self.nature.value,
            "nature_id": self.nature_id
        }

class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    gender = db.Column(db.String(100), unique=False, nullable=True)
    hair_color = db.Column(db.String(100), unique=False, nullable=True)
    eye_color = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "hair_color": self.hair_color,
            "eye_color": self.eye_color
        }

class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=False, nullable=False)
    population = db.Column(db.Integer, unique=False, nullable=True)
    terrain = db.Column(db.String(100), unique=False, nullable=True)

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain
        }
    