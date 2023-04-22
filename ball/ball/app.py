from flask import Flask, render_template, request, session, flash
from datetime import timedelta
import requests
from flask_sqlalchemy import SQLAlchemy	
from datetime import datetime
from sqlalchemy import Identity 
db = SQLAlchemy()
#imports Flask, SQLAlchemy, requests, render_template and Identity 
#declares db 

app = Flask(__name__)
app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)
db.init_app(app)
#creates an instance of Flask where __name__ is the path given to app 
#app.config creates the URI which is used for the connection

class User(db.Model):
	user_id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
#creates a table with 4 columns:
#user_id as primary key, username, password and date_created 
	def __repr__(self):
		return '<name %r>' % self.id
#returns a string as a representation of the object

class Games(db.Model):
	games_id = db.Column(db.Integer, primary_key=True)
	home_team = db.Column(db.String)
	away_team = db.Column(db.String)
	date = db.Column(db.DateTime, default=datetime.utcnow)
#creates the second table for Games which contains game_id as the primary key, 
# home team, away team and the date for the game
	
User_Favourited = db.Table('favourites',
			   db.Column('user_id', db.Integer, db.ForeignKey('user.user_id')),
			   db.Column('games_id', db.Integer, db.ForeignKey('games.games_id'))
			   )
	
#Creates a third table for favourites in which the user_id and games_id are foreign keys

with app.app_context():
	db.create_all()
#under the context of app, it will create all tables under User.db

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user_in_db = db.session.execute(db.select(User).filter_by(username=username)).scalar()

		if user_in_db is None:
			return render_template("failed.html")
		elif "username" in session:
			flash("Already Logged In!")
			return render_template("login.html")
		else:
			if user_in_db.password == password:
				session.permanent = True
				session["username"] = username
				return render_template("profile.html")
	return render_template("login.html")
#creates a login html template under /login route
#grabs username and password and compares it with the database.
#if username is there then it will return loggedin.html template with all user-enabled features
#if not then it will render the template failed.html
#line 65 checks if the username is already in a session, if so it will flash an error message saying that user is in session


@app.route("/register")
def register():
	return render_template("register.html")
#register template 



@app.route("/api/register", methods=["POST"])
def form():
	username = request.form.get("username")
	password = request.form.get("password")

	user = User(username=username, password=password)
	db.session.add(user)
	db.session.commit()
	return render_template("login.html")
#it will add username and password to user.db database 


@app.route("/") 
def getGames():
	games = requests.get("https://www.balldontlie.io/api/v1/games").json()["data"]


	data = []
	for game in games:
		date = game["date"]
		home_team = game["home_team"]["full_name"]
		visitor_team = game["visitor_team"]["full_name"]

		game_dict = {
			"date": date,
			"home_team": home_team, 
			"visitor_team": visitor_team
		}

		data.append(game_dict)

	return render_template("index.html", data=data)
#this is the homepage, it grabs the api data using a get function and returns it as a json file 
#it will then create a table called data
#for loop is used to increment through the data and return values for specific variables
#creates a dictionary with date, home_team and visitor_team
#renders the template index.html which contains more templating to display the games

@app.route("/logout")
def logout():
	session.pop("username", None)
	return render_template("login.html")
#logs out by removing all session information about username

@app.route("/profile")
def about():
	if "username" in session:
		username = session["username"]
		return render_template("profile.html")
	else: 
		return render_template("login.html")
#checks if username is in session, if it is then display profile.html if not then go back to login page. 

@app.route("/favourites", methods=["POST"])
def favourites():
	home_team = request.form.get("home_team")
	away_team = request.form.get("away_team")
	date = request.form.get("date")


	game = Games(home_team=home_team, away_team=away_team, date=date)
	db.session.add(game)
	db.session.commit
	return render_template("index.html")
	