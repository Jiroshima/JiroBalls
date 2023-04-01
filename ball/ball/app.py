from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy	
from datetime import datetime
from sqlalchemy import Identity 
db = SQLAlchemy()
#imports Flask, SQLAlchemy, requests, render_template and Identity 
#declares db 


class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
#creates a User class and a db with 4 columns:
#id, username, password and date_created 

	def __repr__(self):
		return '<name %r>' % self.id
#returns a string as a representation of the object


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db.init_app(app)
#creates an instance of Flask where __name__ is the path given to app 
#app.config creates the URI which is used for the connection

with app.app_context():
    db.create_all()
#under the context of app, it will create all databases 


@app.route("/profile")
def about():
	return render_template("profile.html")
#creates a html template called profile and creates a route for it

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user_in_db = db.session.execute(db.select(User).filter_by(username=username)).scalar()
		if user_in_db is None:
			print("No user found")
		else:
			if user_in_db.password == password:
				return render_template("loggedin.html")
	return render_template("login.html")
#creates a login html template under /login route
#grabs username and password and compares it with the database.
#if username is there then it will return loggedin.html template with all user-enabled features
#if not then it will print no userfound and return the same template


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