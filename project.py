from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, make_response
import requests

app = Flask(__name__)

# Shows home page
@app.route('/')
@app.route('/home/')
def showHome():
    return render_template('index.html')


# Lists all teams
@app.route('/teams/')
def showTeams():
    return render_template('teams/teams.html')


# Create a new team
@app.route('/team/new/')
def newTeam():
    return render_template('teams/newteam.html')

# Edit a team
@app.route('/team/<int:team_id>/edit/')
def editTeam(team_id):
    return render_template('teams/editteam.html')


# Delete a team
@app.route('/team/<int:team_id>/delete/')
def deleteTeam(team_id):
    return render_template('teams/deleteteam.html')


# Show team players
@app.route('/team/<int:team_id>/')
@app.route('/team/<int:team_id>/players/')
def showPlayers(team_id):
    return render_template('players/players.html')


# Show a player's details
@app.route('/team/<int:team_id>/player/<int:player_id>/')
@app.route('/team/<int:team_id>/player/<int:player_id>/details/')
def showPlayerDetails(team_id, player_id):
    return render_template('players/playerdetails.html')


# Create a new player
@app.route('/team/<int:team_id>/player/new/')
def newPlayer(team_id):
    return render_template('players/newplayer.html')


# Edit player details
@app.route('/team/<int:team_id>/player/<int:player_id>/edit')
def editPlayer(team_id, player_id):
    return render_template('players/editplayer.html')


# Delete a player
@app.route('/team/<int:team_id>/player/<int:player_id>/delete')
def deletePlayer(team_id, player_id):
    return render_template('players/deleteplayer.html')


# Lists all events
@app.route('/events/')
def showEvents():
    return render_template('events/events.html')


# Lists event details
@app.route('/event/<int:event_id>')
def showEventDetails(event_id):
    return render_template('events/eventdetails.html')


# Create new event
@app.route('/event/new/')
def newEvent():
    return render_template('events/newevent.html')


# Edit an event
@app.route('/event/<int:event_id>/edit/')
def editEvent(event_id):
    return render_template('events/editevent.html')


# Delete a event
@app.route('/event/<int:event_id>/delete/')
def deleteEvent(event_id):
    return render_template('events/deleteevent.html')



if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
