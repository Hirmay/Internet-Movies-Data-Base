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

@app.route("/insights")
@admin_only
def insights():
    query = "select get_genre_rating();" 
    cur.execute(query)
    results_genre = cur.fetchall()
    query = "select get_ott_rating();" 
    cur.execute(query)
    results_ott = cur.fetchall()    
    return render_template("insights.html", results_genre=results_genre, results_ott = results_ott)


@app.route("/admin-add", methods=["GET", "POST"])
@admin_only
def admin_add():
    if request.method == "POST":
        movie_id = request.form.get("movie_id")
        title = request.form.get("title")
        production_cost = request.form.get("production_cost")
        rating = request.form.get("rating")
        rated = request.form.get("rated")
        release_date = request.form.get("released_date")
        platform = request.form.get("platform")
        likes = request.form.get("likes")
        runtime = request.form.get("runtime")
        director = request.form.get("director")
        if rating == "R ":
            rating == "R"
        cur.execute("INSERT INTO movie (movie_id, title, production_cost, rating, rated, release_date, platform, likes, runtime, director) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", [movie_id, title, production_cost, rating, rated, release_date, platform, likes, runtime, director])
        con.commit()     
        flash("Movie Added")
        return render_template("admin_add.html")
    else:
        return render_template("admin_add.html")


@app.route("/delete-celebrity", methods=["GET", "POST"])
@login_required
def delete_celebrity():
    person_id = request.args.get('person_id')
    cur.execute("SELECT * FROM celebrity WHERE person_id=%s", [person_id])
    rows = cur.fetchone()
    print(rows)
    if request.method == "POST":
        cur.execute("DELETE FROM celebrity WHERE person_id=%s", [person_id])
        con.commit()
        flash("Celebrity has been deleted")
        return render_template("admin.html", movies=rows, l=len(rows))
    else:
        movie_id = request.args.get('person_id')
        cur.execute("SELECT * FROM celebrity WHERE person_id=%s", [person_id])
        rows = cur.fetchone()
        print(rows)
        #cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
        #rows = cur.fetchone()
        username = session.get("username")
        cur.execute("SELECT date_of_birth FROM db_user WHERE username=%s", [username])
        datee = cur.fetchall()
        query = "SELECT display_celeb_movies( '" + rows[0] + "' , '"+ str(datee[0][0]) + "' );" 
    # cur.execute("CALL search_movie(%s,%s);",[datee[0], search_string])
    # cur.callproc('search_movie',[datee[0], search_string])
    # print(query)
        cur.execute(query)
        results = cur.fetchall()
        print(results)
        if len(results) > 0:
            if len(results) == 1:
                rtuple =  results[0][0] 
                query = "SELECT movie_id, title FROM movie where movie_id in ( '" + rtuple + "' ) ;"
            else:
                rtuple = list()
                for r in results:
                    rtuple.append(r[0])
                rtuple = tuple(rtuple)
                # print(rtuple)
                query = "SELECT movie_id, title FROM movie where movie_id in " + str(rtuple) + " ;"
            # print(query)
            cur.execute(query)
            results = cur.fetchall()
            return render_template("celebrity.html", celebrity=rows, l=len(results), results=results)
        else:
            return render_template("celebrity.html", celebrity=rows, l=0, results=None) 
        
@app.route("/celebrity")
@login_required
def celebrity():
    movie_id = request.args.get('person_id')
    cur.execute("SELECT * FROM celebrity WHERE person_id=%s", [movie_id])
    rows = cur.fetchone()
    print(rows)
    #cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
    #rows = cur.fetchone()
    username = session.get("username")
    cur.execute("SELECT date_of_birth FROM db_user WHERE username=%s", [username])
    datee = cur.fetchall()
    query = "SELECT display_celeb_movies( '" + rows[0] + "' , '"+ str(datee[0][0]) + "' );" 
# cur.execute("CALL search_movie(%s,%s);",[datee[0], search_string])
# cur.callproc('search_movie',[datee[0], search_string])
# print(query)
    cur.execute(query)
    results = cur.fetchall()
    print(results)
    if len(results) == 1:
        rtuple =  results[0][0] 
        query = "SELECT movie_id, title FROM movie where movie_id in ( '" + rtuple + "' ) ;"
    else:
        rtuple = list()
        for r in results:
            rtuple.append(r[0])
        rtuple = tuple(rtuple)
        # print(rtuple)
        query = "SELECT movie_id, title FROM movie where movie_id in " + str(rtuple) + " ;"
    # print(query)
    cur.execute(query)
    results = cur.fetchall()
    return render_template("celebrity.html", celebrity=rows, l=len(results), results=results)



@app.route("/delete-movie", methods=["GET", "POST"])
@login_required
def delete_movie():
    movie_id = request.args.get('movie_id')
    cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
    rows = cur.fetchone()
    #cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
    #rows = cur.fetchone()
    if request.method == "POST":
            cur.execute("DELETE FROM movie WHERE movie_id=%s", [movie_id])
            con.commit()
            flash("Movie has been deleted")
            return render_template("admin.html", movies=rows, l=len(rows))
    else:
        return render_template("delete_movie.html", movies=rows, l=len(rows))
    
@app.route("/movie", methods=["GET", "POST"])
@login_required
def movie():
    cur = con.cursor()
    username = session.get("username")
    movie_id = request.args.get('movie_id')
    cur.execute("SELECT * FROM movie WHERE movie_id=%s", [movie_id])
    rows = cur.fetchone()
    if request.method == "POST":
            try:
                like =  request.form["like"]
                flash("Movie is liked")
                # Insert into queries remaining
            except:
                try:
                    watchlist = request.form["watchlist"]
                    flash("Movie has been added to the watchlist")
                except:
                    review = request.form["review"]
                    # flash(review)
                    cur.execute("SELECT warning from db_user where username=%s", [username])
                    temp = cur.fetchone()
                    print(temp)
                    if temp[0]==None:
                        warns = 0
                    else:
                        warns = temp[0]
                    warns += 1
                    try:
                        cur.execute("SELECT count(*) from movie_review;")
                        review_id = cur.fetchone()[0] + 1
                        # print(review_id)
                        cur.execute("INSERT INTO movie_review(review_id, posted_on, content, up_votes, movie_id, username) VALUES (%s, current_date, %s, 0, %s, %s);", [review_id, review, movie_id, username])
                        con.commit()
                    except Exception as e:
                        # flash(e)
                        con.commit()
                        # cur.open()
                        # cur = con.cursor()
                        flash("Use of abusive language detected. You are given a warining. If your warnings exceed 3 then your account will be banned!")
                        username = session.get("username")
                        query = "UPDATE db_user set warning=" + str(warns) + " where username='" + username + "' ;"
                        print(query)
                        cur.execute(query)
                        con.commit()
                        cur.close()
                        
            return render_template("movie.html", movies=rows, l=len(rows))
    else:
        return render_template("movie.html", movies=rows, l=len(rows))

@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    cur = con.cursor()
    search = Search_M_W(request.form)
    # print(search.data['select'])
    option = search.data['select']
    username = session.get("username")
    if request.method == "POST":
        results = []
        search_string = search.data['search']
        if search.data['search'] != '':
            if option == 'Movie':
                cur.execute("SELECT date_of_birth FROM db_user WHERE username=%s", [username])
                datee = cur.fetchall()
                print(datee)
                print(search_string)
                query = "SELECT search_movies_by_rating( '"+ str(datee[0][0]) + "' , '" + search_string + "' );" 
            # cur.execute("CALL search_movie(%s,%s);",[datee[0], search_string])
            # cur.callproc('search_movie',[datee[0], search_string])
            # print(query)
                cur.execute(query)
                results = cur.fetchall()
                print(results)
                if len(results) > 0:
                    if len(results) == 1:
                        rtuple =  results[0][0] 
                        query = "SELECT movie_id, title FROM movie where movie_id in ( '" + rtuple + "' ) ;"
                    else:
                        rtuple = list()
                        for r in results:
                            rtuple.append(r[0])
                        rtuple = tuple(rtuple)
                        # print(rtuple)
                        query = "SELECT movie_id, title FROM movie where movie_id in " + str(rtuple) + " ;"
                    # print(query)
                    cur.execute(query)
                    results = cur.fetchall()
                else:
                    flash('No results found!')
                    return render_template('search.html', form=search)   
            elif option == 'Celebrity':
                print(search_string)
                query = "SELECT search_celebs( '" + search_string + "' );" 
            # cur.execute("CALL search_movie(%s,%s);",[datee[0], search_string])
            # cur.callproc('search_movie',[datee[0], search_string])
            # print(query)
                cur.execute(query)
                # print(results)
                results = cur.fetchall()
                if len(results) > 0:
                    if len(results) == 1:
                        rtuple =  results[0][0] 
                        query = "SELECT person_id, firstname, lastname FROM celebrity where person_id in ( '" + rtuple + "' ) ;"
                    else:
                        rtuple = list()
                        for r in results:
                            rtuple.append(r[0])
                        rtuple = tuple(rtuple)
                        # print(rtuple)
                        query = "SELECT person_id, CONCAT(firstname, ' ', lastname) FROM celebrity where person_id in " + str(rtuple) + " ;"
                    # print(query)
                    cur.execute(query)
                    results = cur.fetchall()
                else:
                    flash('No results found!')
                    return render_template('search.html', form=search)       
            else:
                cur.execute("SELECT date_of_birth FROM db_user WHERE username=%s", [username])
                datee = cur.fetchall()
                print(datee)
                print(search_string)
                query = "SELECT search_movies( '"+ str(datee[0][0]) + "' , '" + search_string + "' );" 
            # cur.execute("CALL search_movie(%s,%s);",[datee[0], search_string])
            # cur.callproc('search_movie',[datee[0], search_string])
            # print(query)
                cur.execute(query)
                # print(results)
                results = cur.fetchall()
            
            # flash(results)
            # Run query to see results
        if not results:
            flash('No results found!')
            return render_template('search.html', form=search)
        else:
            l = len(results)
            print(results)
            return render_template('searched.html', results=results, form=search, option=option, l=l) 
    else:
        return render_template("search.html", form=search)
    
    
@app.route('/searched')
def searched(search):
    cur = con.cursor()
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
    cur = con.cursor()
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
    cur = con.cursor()
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
