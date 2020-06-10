import csv
import os
import pdb

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
# app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://postgres:USE_YOUR_PASSWORD@db:5432/flaskapp_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
db.init_app(app)

def get_author_id(author_name, author_list):
 for a in author_list:
    if a.name == author_name:
        return a.id

def insert_authors(reader):
    authors = []
    for isbn, title, author, year in reader:
        if author not in authors:
            authors.append(author)

    for author in authors:
        name = Author(name=author)
        db.session.add(name)
        print(name)
    db.session.commit()

def insert_books(reader):
    f = open("../books.csv")
    reader = csv.reader(f)
    all_authors = Author.query.all()

    for isbn, title, author, year in reader:
        author_id = get_author_id(author, all_authors)
        book = Book(isbn=isbn, title=title, author_id=author_id, year=year)
        db.session.add(book)
        print(book)
    db.session.commit()


def main():
    f = open("../books.csv")
    reader = csv.reader(f)

    insert_authors(reader)
    insert_books(reader)


if __name__ == "__main__":
    with app.app_context():
        main()

