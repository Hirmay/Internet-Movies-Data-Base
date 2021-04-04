from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from flask_migrate import Migrate

app = Flask(__name__)

# Session = sessionmaker(bind = engine)
# session = Session()

# IMPORTANT
# APP_SETTINGS = "config.DevelopmentConfig"
# DATABASE_URL="postgresql://postgres:tirth177@localhost/mwdb"
# app.config.from_object(APP_SETTINGS)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Change this your postes will be linked
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:tirth177@localhost/mwdb"

db = SQLAlchemy(app)
# migrate = Migrate(app, db)

# @app.route("/")
# def hello():
#     return "Hello"

class db_user(db.Model):
    __tablename__ = 'db_user'

    email = db.Column(db.String(50),primary_key=True, nullable=False)
    username = db.Column(db.String(20), unique=True)
    firstname = db.Column(db.String(20), nullable = False)
    lastname = db.Column(db.String(20), nullable = False)
    hashh = db.Column(db.String(100), nullable = False)

    def __init__(self, email, username, firstname, hashh):
        self.email = email
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.hashh = hashh

    def __repr__(self):
        return '<username {}>'.format(self.username)
    
    def serialize(self):
        return {
            'email': self.email, 
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'hashh': self.hashh
        }


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
        rows = db.execute("SELECT * FROM db_user WHERE username=?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)
        # Remembering the session id
        db.session["user_id"] = rows[0]["id"]
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
        rows = db.execute("SELECT * FROM users WHERE username=?", username)

        if len(rows) != 0:
            return apology("Username is Taken", 403)

        elif password != password_confirm:
            return apology("Passwords don't match")

        # Generating password hash to store in db
        password_hash = generate_password_hash(password)

        # Adding the new user to database
        db.execute("INSERT INTO users (first_name, last_name, username, email_id, hash) VALUES(?,?,?,?,?)", first_name,last_name, username, email_id, password_hash)

        # Now extracting the user id
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        db.session["user_id"] = rows[0]["id"]
        db.session["name"] = rows[0]["first_name"]
        flash("Welcome " + db.session.get("name"))

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/getall")
def get_all():
    try:
        books= db_user.query.all()
        return  jsonify([e.serialize() for e in books])
    except Exception as e:
	    return(str(e))

if __name__ == '__main__':
    app.run()