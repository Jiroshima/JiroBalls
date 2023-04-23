from flask import Flask, jsonify, redirect, render_template, request, session, flash
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
user_favourited = db.Table('favourites',
			   db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
			   db.Column('game_id', db.Integer, db.ForeignKey('game.id'))
			   )
#eCreats a third table for favourites in which the user_id and games_id are foreign keys

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String, unique = True, nullable = False)
	password = db.Column(db.String, nullable = False)
	date_created = db.Column(db.DateTime, default=datetime.utcnow)
	games = db.relationship("Game", secondary=user_favourited, backref='games')
#creates a table with 4 columns:
#user_id as primary key, username, password and date_created 
	def __repr__(self):
		return '<name %r>' % self.id
#returns a string as a representation of the object

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	home_team = db.Column(db.String)
	away_team = db.Column(db.String)
	date = db.Column(db.DateTime, default=datetime.utcnow)
	
#creates the second table for Games which contains game_id as the primary key, 
# home team, away team and the date for the game
#Line 42 creates the relationship between game and users and adds user_favourited as the association table 
	

with app.app_context():
	db.create_all()
#under the context of app, it will create all tables under User.db

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "GET":
		if "username" in session:
			return redirect("/profile", code=302)
		return render_template("login.html")
	# if the username is in session and tries to access the /login page through the 'get' method; or in otherwords manually inputting the link while a user is in session
	# then it will simply redirect to the /profile url 
	
	
	if request.method == "POST":
		username = request.form.get("username")
		password = request.form.get("password")
		user_in_db = db.session.execute(db.select(User).filter_by(username=username)).scalar()

		if user_in_db is None:
			flash("Incorrect username or password")
			return render_template("login.html")
		else:
			if user_in_db.password == password:
				session.permanent = True
				session["username"] = username
				session["user_id"] = user_in_db.id
				print(session)
				return redirect("/", code=302)
	
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
		id = game["id"]
		date = game["date"]
		home_team = game["home_team"]["full_name"]
		away_team = game["visitor_team"]["full_name"]

		game_dict = {
			"id": id,
			"date": date,
			"home_team": home_team, 
			"away_team": away_team
		}

		data.append(game_dict)

	favourites = [g["id"] for g in getFavourites().json]
	
	return render_template("index.html", data=data, favourites=favourites)
#this is the homepage, it grabs the api data using a get function and returns it as a json file 
#it will then create a table called data
#for loop is used to increment through the data and return values for specific variables
#creates a dictionary with date, home_team and visitor_team
#renders the template index.html which contains more templating to display the games

@app.route("/logout")
def logout():
	session.clear()
	return render_template("login.html")
#logs out by removing all session information about username

@app.route("/profile")
def about():
	if "user_id" in session:
		games = getFavourites()
		return render_template("profile.html", games=games)
	else: 
		return render_template("login.html")
#checks if username is in session, if it is then display profile.html if not then go back to login page. 

@app.route("/add-favourite", methods=["POST"])
def addfavourite():
	
	user_id = request.form.get("user_id")
	game_id = request.form.get("game_id")
	home_team = request.form.get("home_team")
	away_team = request.form.get("away_team")
	game_date = request.form.get("game_date")
	game_datetime = datetime.strptime(game_date, '%Y-%m-%d')
	
	
	if "user_id" in session: 
		game = db.session.execute(db.select(Game).filter_by(id=game_id)).scalar()
		if game is None:
			game = Game(id=game_id, home_team=home_team, away_team=away_team, date=game_datetime)
			db.session.add(game)
			db.session.commit()
			
		user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
		print(user)
		user.games.append(game)
		db.session.commit()
	return redirect("/", code=302)

#This creates an app route called add-favourite
#It takes the method post and grabs values for the variables specified and stores them in the table
#if the favourite button from the index.html is pressed
#the If statement is used to check if the data is already in the database, if it is
#then it just renders the template index.html 
	
	
@app.route("/get-favourites", methods=["GET"])
def getFavourites():
		
	def gameToDict(game):
		return {
			"id": game.id,
			"date": game.date,
			"home_team": game.home_team, 
			"away_team": game.away_team
		}
	
	if "user_id" in session:
		user_id = session["user_id"]

		games = Game.query.join(user_favourited).join(User).filter((user_favourited.c.user_id == User.id) & (user_id == user_favourited.c.user_id)).all()
		return(jsonify(list((map(gameToDict, games)))))
	
	else:
		return redirect("/", code=302)

		



