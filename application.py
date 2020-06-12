import os, requests, datetime
import config

from flask import g, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy

from models import *

db.init_app(app)

app.secret_key = 'somesecretkey'

@app.before_request
def before_request():
    if 'logged_in' not in session and request.endpoint != 'login' and request.endpoint != 'signup':
        return redirect(url_for('login'))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST","GET"])
def signup():

    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        ## TODO -> better logic to OR
        u_username = User.query.filter_by(username=username).first()
        u_email = User.query.filter_by(email=email).first()

        if u_username is None and u_email is None:
            signup = User(username=username, email=email, date_signed_up=datetime.datetime.now(), password=password)
            db.session.add(signup)
            db.session.commit()
            return render_template("success.html", username=username)

        return "this user is alredy in use"

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.pop('logged_in', None)

        username = request.form.get("username")
        password = request.form.get("password")

        ## TODO -> better logic to OR
        u_username = User.query.filter_by(username=username).first()
        u_password = User.query.filter_by(password=password).first()

        if u_username is not None and u_password is not None:
            session['logged_in'] = u_username.id
            return redirect(url_for('search'))

    return render_template("login.html")

@app.route("/search",methods=["POST","GET"])
def search():
    if request.method == "POST":
        query = request.form.get("query")
        search = "%{}%".format(query)
        books = Book.query.join(Author)\
            .filter(or_(Book.title.ilike(search),Book.isbn.ilike(search),Author.name.ilike(search)))\
            .all()

    return render_template("search.html", books=books)

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('logged_in', None)

    return redirect(url_for('login'))


@app.route("/reviews")
def reviews():
    url = "https://www.goodreads.com/book/review_counts.json"
    r = requests.get(url, params={'isbns': "1476733503"})

    return r.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
