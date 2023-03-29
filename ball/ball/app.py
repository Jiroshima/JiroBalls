import select
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


@app.route('/')
def index():
	return render_template("index.html")	


@app.route("/profile")
def about():
	return render_template("profile.html")
	
@app.route("/register")
def register():
	return render_template("register.html")

@app.route("/api/register", methods=["POST"])
def add_user():
	username = request.form.get("username")
	password = request.form.get("password")

	user = User(username=username, password=password)
	db.session.add(user)
	db.session.commit()

	return render_template("login.html")

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user_in_db = db.session.execute(db.select(User).filter_by(username=username)).scalar()
		print(user_in_db)
		if user_in_db is None:
			print("No user found")
		else:
			if user_in_db.password == password:
				return render_template("loggedin.html")
 
	return render_template("login.html")


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
