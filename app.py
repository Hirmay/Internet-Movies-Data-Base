from flask import Flask, render_template, request, redirect, jsonify, session, flash
import psycopg2
# from Flask-Session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from classes import *


# from flask_migrate import Migrate

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# IMPORTANT
con = psycopg2.connect(
    database = 'mwdb',
    user = 'postgres',
    password = '123ketki',
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

# Admin only redirection
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("username") != "admin":
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
    cur.execute("SELECT * FROM movie;")
    # row = cur.fetchone()
    rows = cur.fetchall()
    return render_template("index.html", movies=rows, l=len(rows))

    # flash(e, "error")
    

@app.route("/error")
def show_error():
    try:
        cur.execute("call error_gen();")
    except Exception as e:
        s = e
    flash(s)
    return render_template('show_error_temp.html')


@app.route("/admin")
@admin_only
def admin():
    return render_template("admin.html")

@app.route("/admin-add")
@admin_only
def admin_add():
    search = ADD_M_W(request.form)
    
    if request.method == "POST":
        results = []
        search_string = search.data['search']
        if search.data['search'] == '':
            results = 'abc'
            # Run query to see results
        if not results:
            flash('No results found!')
            return render_template('admin_add.html', form=search)
        else:
            # display results
            return render_template('searched.html', results=results, form=search) 
    else:
        return render_template("admin_add.html", form=search)

@app.route("/admin-delete")
@admin_only
def admin_delete():
    search = DELETE_M_W(request.form)
    
    if request.method == "POST":
        results = []
        search_string = search.data['search']
        if search.data['search'] == '':
            results = 'abc'
            # Run query to see results
        if not results:
            flash('No results found!')
            return render_template('admin_delete.html', form=search)
        else:
            # display results
            return render_template('delete_searched.html', results=results, form=search) 
    else:
        return render_template("admin_delete.html", form=search)    
    
@app.route("/movie", methods=["GET", "POST"])
@login_required
def movie():
    movie_id = request.args.get('movie_id')
    cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
    rows = cur.fetchall()
    if request.method == "POST":
        return apology("Page not created", 404)
    else:
        return render_template("movie.html", movies=rows, l=len(rows))

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    search = Search_M_W(request.form)
    
    if request.method == "POST":
        results = []
        search_string = search.data['search']
        if search.data['search'] == '':
            results = 'abc'
            # Run query to see results
        if not results:
            flash('No results found!')
            return render_template('search.html', form=search)
        else:
            # display results
            return render_template('searched.html', results=results, form=search) 
    else:
        return render_template("search.html", form=search)
    
    
@app.route('/searched')
def searched(search):
    results = []
    search_string = search.data['search']
    if search.data['search'] == '':
        results = 'abc'
        # Run query to see results
    if not results:
        flash('No results found!')
        return render_template('searched.html',results=results, form=search)
    else:
        # display results
        return render_template('searched.html', results=results, form=search)    

@app.route("/login", methods=["GET", "POST"])
def login():

    # forgets any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        username = username.lower()
        password = request.form.get("password")

        # Checking if the username or password are correct or not
        
        cur.execute("SELECT * FROM db_user WHERE username=%s", [username])
        rows = cur.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][5], password):
            return apology("Invalid username and/or password", 403)
        
        # Remembering the session id
        session["username"] = rows[0][1]
        flash("Welcome Back " + rows[0][3])
        
        # Checking if the user is admin
        if rows[0][1] == "admin":
            return redirect("/admin")
        
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
        dob = request.form.get("dob")
        username = request.form.get("username")
        email_id = request.form.get("email_id")
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")
        
        # Checking if the username is already taken
        cur.execute("SELECT * FROM db_user WHERE username=%s", [username])

        rows = cur.fetchall()

        if len(rows) != 0:
            return apology("Username is Taken", 403)

        elif password != password_confirm:
            return apology("Passwords don't match")

        # Generating password hash to store in db
        password_hash = generate_password_hash(password)

        # Adding the new user to database
        cur.execute("INSERT INTO db_user (firstname, lastname, date_of_birth, username, email, hash) VALUES(%s,%s,%s,%s,%s,%s)", [first_name,last_name, dob, username, email_id, password_hash])
        con.commit()
        # Now extracting the user id
        
        cur.execute("SELECT * FROM db_user WHERE username=%s", [username])
        rows = cur.fetchall()
        # print(rows)
        session["username"] = rows[0][1]
        session["name"] = rows[0][3]
        flash("Welcome " + session.get("name"))

        return redirect("/")
    else:
        return render_template("register.html")

@app.route("/logout")
def logout():
    # logs out users
    session.clear()
    return redirect("/")
    
# @app.route('\show')
# def show():


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.debug = True
    app.run()