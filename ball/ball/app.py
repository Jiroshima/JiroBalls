from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usernames.db'
db = SQLAlchemy(app)


class usernames(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(200), nullable = False)
	date_created = db.column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<name %r>' % self.id

Users = []



@app.route('/')
def index():
	return render_template("index.html")	


@app.route("/profile")
def about():
	return render_template("profile.html")

@app.route("/login")
def login():
	return render_template("login.html")

@app.route("/form", methods=["POST"])
def form():
	Username = request.form.get("Username")
	Password = request.form.get("Password")
	Users.append(f"{Username} || {Password}")
	return render_template("form.html", Users=Users)

@app.route("/api/games") 
def getGames():
	games = requests.get("https://www.balldontlie.io/api/v1/games").json()["data"]


	result = []
	for game in games:
		date = game["date"]
		home_team = game["home_team"]["full_name"]
		visitor_team = game["visitor_team"]["full_name"]

		game_dict = {
			"date": date,
			"home_team": home_team, 
			"visitor_team": visitor_team
		}

		result.append(game_dict)

	return(result)
