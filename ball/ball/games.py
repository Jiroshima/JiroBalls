import requests

games = requests.get("https://www.balldontlie.io/api/v1/games").json()["data"]


result = []

print([
    {
        "date": game["date"],
        "home_team": game["home_team"]["full_name"],
        "visitor_team": game["visitor_team"]["full_name"]
    } for game in games])