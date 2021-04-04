from flask import Flask, render_template, request, redirect, jsonify, session
import psycopg2
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)


# IMPORTANT
con = psycopg2.connect(
    database = 'mwdb',
    user = 'postgres',
    password = 'tirth177',
    host = 'localhost',
)

# Cursor Testing
cur = con.cursor()
print('Postgres Version: ')
cur.execute("Select version()")
db_version = cur.fetchone()
print(db_version)


# @app.route("/")
# def hello():
#     return "Hello"

# class db_user(db.Model):
#     __tablename__ = 'db_user'

#     email = db.Column(db.String(50),primary_key=True, nullable=False)
#     username = db.Column(db.String(20), unique=True)
#     firstname = db.Column(db.String(20), nullable = False)
#     lastname = db.Column(db.String(20), nullable = False)
#     hashh = db.Column(db.String(100), nullable = False)

#     def __init__(self, email, username, firstname, hashh):
#         self.email = email
#         self.username = username
#         self.firstname = firstname
#         self.lastname = lastname
#         self.hashh = hashh

#     def __repr__(self):
#         return '<username {}>'.format(self.username)
    
#     def serialize(self):
#         return {
#             'email': self.email, 
#             'username': self.username,
#             'firstname': self.firstname,
#             'lastname': self.lastname,
#             'hashh': self.hashh
#         }


# Login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") is None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # forgets any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        username = username.lower()
        password = request.form.get("password")

        # Checking if the username or password are correct or not
        rows = cur.execute("SELECT * FROM db_user WHERE username=?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)
        # Remembering the session id
        session["username"] = rows[0]["username"]
        flash("Welcome Back " + rows[0]["first_name"])

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # forgets any user
    session.clear()

    if request.method == "POST":
        # Checking for name

        # Assigning values to save time
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        username = request.form.get("username")
        email_id = request.form.get("email_id")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # Checking if the username is already taken
        rows = cur.execute("SELECT * FROM db_user WHERE username=?", username)

        if len(rows) != 0:
            return apology("Username is Taken", 403)

        elif password != password_confirm:
            return apology("Passwords don't match")

        # Generating password hash to store in db
        password_hash = generate_password_hash(password)

        # Adding the new user to database
        cur.execute("INSERT INTO db_user (first_name, last_name, username, email_id, hash) VALUES(?,?,?,?,?)", first_name,last_name, username, email_id, password_hash)

        # Now extracting the user id
        rows = cur.execute("SELECT * FROM db_user WHERE username=?", username)
        session["username"] = rows[0]["username"]
        session["name"] = rows[0]["first_name"]
        flash("Welcome " + session.get("name"))

        return redirect("/")
    else:
        return render_template("register.html")


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run()