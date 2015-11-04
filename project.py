from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
import requests

app = Flask(__name__)

# Shows home page
@app.route('/')
@app.route('/home/')
def showHome():
    return "This will show the home page."


# Lists all teams
@app.route('/teams/')
def showTeams():
    return "This will list all teams"


# Create a new team
@app.route('/team/new/')
def newTeam():
    return "This will add new team"

# Edit a team
@app.route('/team/<int:team_id>/edit/')
def editTeam(team_id):
    return "This will edit team"


# Delete a team
@app.route('/team/<int:team_id>/delete/')
def deleteTeam(team_id):
    return "This will delete team"


# Show team players
@app.route('/team/<int:team_id>/')
@app.route('/team/<int:team_id>/players/')
def showPlayers(team_id):
    return "This will list all the players in a list"


# Show a team players
@app.route('/team/<int:team_id>/player/<int:player_id>/')
@app.route('/team/<int:team_id>/player/<int:player_id>/details/')
def showPlayerDetails(team_id, player_id):
    return "This will show players details"


# Create a new player
@app.route('/team/<int:team_id>/player/new/')
def newPlayer(team_id):
    return "This will add new player"


# Edit player details
@app.route('/team/<int:team_id>/player/<int:player_id>/edit')
def editPlayer(team_id, player_id):
    return "This will edit player details"


# Delete a player
@app.route('/team/<int:team_id>/player/<int:player_id>/delete')
def deletePlayer(team_id, player_id):
    return "This will delete player from a team"


# Lists all events
@app.route('/events/')
def showEvents():
    return "This will list all the upcoming events"


# Lists event details
@app.route('/event/<int:event_id>')
def showEventDetails(event_id):
    return "This will show event details"


# Create new event
@app.route('/event/new/')
def newEvent():
    return "This will create new event"


# Edit an event
@app.route('/event/<int:event_id>/edit/')
def editEvent(event_id):
    return "This will edit an event"


# Delete a player
@app.route('/event/<int:event_id>/delete/')
def deleteEvent(event_id):
    return "This will delete upcoming event"



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
