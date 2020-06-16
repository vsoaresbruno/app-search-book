import os, requests, datetime, json
import config

from flask import redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_sqlalchemy import SQLAlchemy

from models import *

engine = create_engine(os.getenv("DATABASE_URL"))
db.init_app(app)
app.secret_key = 'somesecretkey'
db = scoped_session(sessionmaker(bind=engine))

def get_review_goodreaders(isbn):
    url = "https://www.goodreads.com/book/review_counts.json"
    resp = requests.get(url, params={'isbns': isbn})
    if resp.status_code != 200:
        raise Exception("ERROR: API request unsuccessful.")
    data = resp.json()

    return data

def get_user_id():
    session_id = session['logged_in']
    user = db.execute("SELECT * FROM users WHERE id = :id",
                        {"id": session_id}).fetchone()

    return user.id

def handle_avg_decimal(average):
   for value in average:
        for avg in value:
            return str(avg)

def handle__sum(total_sum):
      for total in total_sum:
        for value in total:
            return value

@app.before_request
def before_request():
    if 'logged_in' not in session and request.endpoint != 'login' and request.endpoint != 'signup':
        return redirect(url_for('login'))

@app.route("/")
def index():
    user_id = get_user_id()

    if user_id is not None:
        return redirect(url_for('search'))
    return render_template("index.html")

@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.execute("SELECT id FROM users WHERE username = :username OR email = :email",
                                {"username": username, "email": email}).fetchone()

        if user is None:
            db.execute("INSERT INTO users (username, email, date_signed_up, password) VALUES (:username, :email, :date_signed_up, :password)",
                   {"username": username, "email": email, "date_signed_up": datetime.datetime.now(), "password": password})
            db.commit()
            return render_template("success.html", username=username)

        return "this user is alredy in use"

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.pop('logged_in', None)

        username = request.form.get("username")
        password = request.form.get("password")

        user = db.execute("SELECT id FROM users WHERE username = :username AND password = :password",
                                {"username": username, "password": password}).fetchone()

        if user is not None:
            session['logged_in'] = user['id']
            return redirect(url_for('search'))

    return render_template("login.html")

@app.route("/logout", methods=["GET"])
def logout():
    session.pop('logged_in', None)

    return redirect(url_for('login'))

@app.route("/search",methods=["POST","GET"])
def search():
    if request.method == "POST":
        query = request.form.get("query")
        search = "%{}%".format(query)

        books = db.execute("SELECT b.title, b.id, b.author_id, b.isbn, authors.name FROM books b INNER JOIN authors ON b.author_id=authors.id WHERE b.title ILIKE :search_title OR authors.name ILIKE :search_author OR b.isbn ILIKE :search_isbn",
        {"search_title": search, "search_author": search, "search_isbn": search}).fetchall()

        return render_template("search.html", books=books)

    return render_template("search.html")

@app.route("/book/<int:book_id>", methods=["POST","GET"])
def book(book_id):
    if request.method == "POST":
        user_id = get_user_id()
        reviewed = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id",
                                {"user_id": user_id, "book_id": book_id}).fetchone()

        if reviewed is None:
            review_rating = request.form.get("review")
            review_opnion = request.form.get("review_opnion")

            db.execute("INSERT INTO reviews (review, review_opnion, book_id, user_id) VALUES (:review, :review_opnion, :book_id, :user_id)",
                   {"review": review_rating, "review_opnion": review_opnion, "book_id": book_id, "user_id": user_id})
            db.commit()

            return "Reviewed"
        return "Sorry"

    book = db.execute("SELECT b.title, b.id, b.author_id, b.year, b.isbn, authors.name FROM books b INNER JOIN authors ON b.author_id=authors.id WHERE b.id = :id",
                        {"id": book_id}).fetchone()

    if book is None:
        return render_template("error.html", message="No such book.")

    data = get_review_goodreaders(book["isbn"])
    average_rating = data["books"][0]["average_rating"]

    return render_template("book_detail.html", book=book, average_rating=average_rating)


@app.route("/api/<string:isbn>")
def books_api(isbn):
    book = db.execute("SELECT b.title, b.id, b.author_id, b.year, b.isbn, authors.name FROM books b INNER JOIN authors ON b.author_id=authors.id WHERE isbn = :isbn ",{"isbn": isbn}).fetchone()


    avg_query = db.execute("SELECT round(AVG(review),2) FROM reviews WHERE book_id = :book_id",
                            {"book_id": book["id"]}).fetchall()

    sum_query = db.execute("SELECT COUNT(*) FROM reviews WHERE book_id = :book_id",
                            {"book_id": book["id"]}).fetchall()

    total_reviews = handle__sum(sum_query)
    average_score = handle_avg_decimal(avg_query)

    if book is None:
        return jsonify({"error": "Invalid isbn"}), 422
    return jsonify({
            "title": book["title"],
            "author": book.name,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": total_reviews,
            "average_score": average_score
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
