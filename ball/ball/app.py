from flask import Flask, render_template, request
import requests
from flask_sqlalchemy import SQLAlchemy	
from datetime import datetime
from sqlalchemy import Identity 
db = SQLAlchemy()

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)

	def __repr__(self):
		return '<name %r>' % self.id


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db.init_app(app)

with app.app_context():
    db.create_all()


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
