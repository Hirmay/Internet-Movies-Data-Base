from cs50 import SQL

from flask import Flask, flash, request, render_template, redirect, jsonify, session
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from tempfile import mkdtemp
import datetime

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Assigning farmer .db
db = SQL("sqlite:///farmer.db")


# Building the login_required
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function


# also helps escaping special characters to avoid sql inject attacks
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


# the default page
@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/info")
@login_required
def info():
    # Implement a slideshow to give them information
    return render_template("info.html")


@app.route("/loan", methods=["GET", "POST"])
@login_required
def loan():
    if request.method == "POST":
        # Show them info and a link to get loan
        amount = int(request.form.get("amount"))
        years = int(request.form.get("years"))
        # Calculating interest
        pay_amount = (amount) * ((1.085) ** years)
        # Getting the current
        now = datetime.datetime.now()

        date = int(now.strftime('%Y%m%d'))
        # Creating the date before amount to be paid.
        date_future = date + (years * 10000)
        # have to create a database
        db.execute("INSERT INTO time (id, loan, loan_paid, date, date_before) VALUES(?,?,?,?,?)",
                   session.get("user_id"), amount, pay_amount, date, date_future)
        flash("Got a Loan")
        return redirect("/")
    else:
        time = db.execute("SELECT * FROM time WHERE id=?", session.get("user_id"))
        if not time:
            return render_template("loan.html")
        else:
            # caculating before date

            return render_template("loaned_already.html")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    # show them the table of price of vegetable
    if request.method == "POST":
        # Here i have already implemented the pattern={ so that apology isn't required
        # Getting all the values
        state = request.form.get("state")
        district = request.form.get("district")
        market = request.form.get("market")
        commodity = request.form.get("commodity")
        variety = request.form.get("variety")
        # Getting the details
        info_table = db.execute("SELECT min_price, max_price, modal_price FROM prices WHERE state LIKE ? AND district LIKE ? AND market LIKE ? AND commodity LIKE ? AND variety LIKE ?",
                                "{}%".format(state), "{}%".format(district), "{}%".format(market), "{}%".format(commodity), "{}%".format(variety))
        if not info_table:
            return apology("Please correctly enter the details")
        return render_template("quoted.html", info_table=info_table, commodity=commodity, variety=variety)
    else:
        return render_template("quote.html")


@app.route("/debts")
@login_required
def history():
    # basically for showing their loan receipts
    time = db.execute("SELECT * FROM time WHERE id=?", session.get("user_id"))
    if not time:
        return render_template("debts.html")
    else:
        # caculating before date
        date_before = str(time[0].get("date_before"))
        date = date_before[6:8]
        month = date_before[4:6]
        year = date_before[0:4]
        date_future = str(date) + "-" + str(month) + "-" + str(year)
        return render_template("loaned.html", time=time, date_future=date_future)


@app.route("/login", methods=["GET", "POST"])
def login():

    # forgets any user id
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        username = username.lower()
        password = request.form.get("password")

        # Checking if the username or password are correct or not
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)
        # Remembering the session id
        session["user_id"] = rows[0]["id"]
        flash("Welcome Back " + rows[0]["name"])

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
        name = request.form.get("name")
        username = request.form.get("username")
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
        db.execute("INSERT INTO users (name, username, hash) VALUES(?,?,?)", name, username, password_hash)

        # Now extracting the user id
        rows = db.execute("SELECT * FROM users WHERE username=?", username)
        session["user_id"] = rows[0]["id"]
        session["name"] = rows[0]["name"]
        flash("Welcome " + session.get("name"))

        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    # logs out users
    session.clear()
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)