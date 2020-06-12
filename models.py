import os, datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
	__tablename__ ="users"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(10), nullable=False)
	email = db.Column(db.String(100), nullable=False)
	date_signed_up = db.Column(db.DateTime())
	password = db.Column(db.String(8), nullable=False)


class Book(db.Model):
	__tablename__ = "books"
	id = db.Column(db.Integer, primary_key=True)
	isbn = db.Column(db.String, nullable=False)
	title = db.Column(db.String, nullable=False)
	author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
	year = db.Column(db.String, nullable=False)
	authors = db.relationship("Author", backref="book", lazy=True)



class Author(db.Model):
	__tablename__ = "authors"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String, nullable=False)

