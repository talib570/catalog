from flask import Flask, render_template, jsonify, url_for, flash
from flask import session as login_session
from flask import make_response, request, redirect

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Game, Player, Team, User
import helper

from werkzeug import secure_filename
import random, string, json, httplib2, requests, os, datetime, json
from time import localtime, strftime

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError

UPLOAD_FOLDER = 'static/images/userimages/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Team player Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///teamcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code, now compatible with Python3
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    # Submit request, parse response - Python3 compatible
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print login_session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        flash("You have successfully been logged out.")
        login_session.clear()
        return redirect(url_for('showTeams'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showTeams'))


# JSON APIs to view Teams Information
@app.route('/team/<int:team_id>/players/JSON')
def teamPlayerJSON(team_id):
    team = session.query(Team).filter_by(id=team_id,is_delete='0').one()
    players = session.query(Player).filter_by(is_delete='0').all()
    return jsonify(Players=[i.serialize for i in players])


@app.route('/team/<int:team_id>/player/<int:player_id>/JSON')
def playerJSON(team_id, player_id):
    player = session.query(Player).filter_by(id=player_id,is_delete='0').one()
    return jsonify(Player=player.serialize)


@app.route('/teams/JSON')
def teamsJSON():
    teams = session.query(Team).filter_by(is_delete='0').all()
    return jsonify(teams=[team.serialize for team in teams])


# Show all teams
@app.route('/')
@app.route('/teams/')
def showTeams():
    teams = session.query(Team).filter_by(is_delete='0').order_by(asc(Team.name))
    if 'username' not in login_session:
        return render_template('teams/teams.html', teams=teams)
    else:
        return render_template('teams/teams.html', teams=teams)


# Create a new team
@app.route('/team/new/', methods=['GET', 'POST'])
def newTeam():
    if 'username' not in login_session:
        return redirect('/login')
    games = session.query(Game)
    if request.method == "POST":
        file = request.files['logo']
        if file and helper.allowed_file(file.filename):
            extension = file.filename.rsplit('.' ,1)
            filename = secure_filename(file.filename)
            filename = helper.hash_filename(filename)+"."+extension[1]
            # saves file in file system
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = 'no_logo.jpg'
        strdate = request.form['start_year'].rsplit('/', 1)
        dateObj = datetime.datetime.strptime(strdate[1], "%Y").date()
        newTeam = Team(
            name=request.form['name'],
            locallity=request.form['locallity'],
            logo=filename,
            start_year=dateObj,
            game_id=request.form['game_id'],
            created_on=datetime.datetime.strptime(strftime("%Y-%m-%d %H:%M:%S", localtime()), "%Y-%m-%d %H:%M:%S"),
            created_by=login_session['user_id'],
            is_active='1' if request.form['status'] == 'Active' else '0',
            is_delete='0',
            )
        session.add(newTeam)
        session.commit()
        flash('New Team %s Successfully Created' % newTeam.name)
        return redirect(url_for('showTeams'))
    else:
        return render_template('teams/newteam.html', games=games)


@app.route('/team/<int:team_id>/removeTeamLogo', methods=["GET", "POST"])
def removeTeamLogo(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        team = session.query(Team).filter_by(id=team_id).one()
        if team.logo != 'no_logo.jpg':
            os.remove(team.logo) if os.path.exists(team.logo) else None
        team.logo = 'no_logo.jpg'
        session.add(team)
        session.commit()
        return jsonify(status=True)
    else:
        return "Remove implementation"


@app.route('/player/<int:player_id>/removePlayerPicture', methods=["GET", "POST"])
def removePlayerPicture(player_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        player = session.query(Player).filter_by(id=player_id).one()
        if player.picture != 'no_picture.jpg':
            os.remove(player.picture) if os.path.exists(player.picture) else None
        player.picture = 'no_picture.jpg'
        session.add(player)
        session.commit()
        return jsonify(status=True)
    else:
        return "Remove implementation"


# Edit a team
@app.route('/team/<int:team_id>/edit/', methods=["GET", "POST"])
def editTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    if team.created_by != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this team. Please create your own team in order to edit.');}</script><body onload='myFunction()''>"
    if request.method=="POST":
        team.name=request.form['name']
        team.locallity=request.form['locallity']
        team.game_id=request.form['game_id']
        team.is_active='1' if request.form['status'] == 'Active' else '0'
        team.name=request.form['name']
        if team.logo != request.files['logo']:
            file = request.files['logo']
            if file and helper.allowed_file(file.filename):
                extension = file.filename.rsplit('.' ,1)
                filename = secure_filename(file.filename)
                filename = helper.hash_filename(filename)+"."+extension[1]
                team.logo = filename
                # saves file in file system
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session.add(team)
        session.commit()
        flash('Team Successfully Edited %s' % team.name)
        return redirect(url_for('showTeams'))
    else:
        games= session.query(Game)
        return render_template('teams/editteam.html', team=team, games=games)


# Delete a team
@app.route('/team/<int:team_id>/delete/', methods=["GET", "POST"])
def deleteTeam(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    team = session.query(Team).filter_by(id=team_id).one()
    if team.created_by != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this team. Please create your own team in order to delete.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        team = session.query(Team).filter_by(id=team_id).one()
        team.is_delete = '1'
        session.add(team)
        session.commit()
        flash('%s Successfully Deleted' % team.name)
        return redirect(url_for('showTeams'))
    else:
        return render_template('teams/deleteteam.html', team=team)


# Show team players
@app.route('/team/<int:team_id>/')
@app.route('/team/<int:team_id>/players/')
def showPlayers(team_id):
    players = session.query(Player).filter_by(team_id=team_id, is_delete='0')
    team = session.query(Team).filter_by(id=team_id).one()
    return render_template('players/players.html', players=players, team=team)


# Create a new player
@app.route('/team/<int:team_id>/player/new/', methods=["GET", "POST"])
def newPlayer(team_id):
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        file = request.files['picture']
        if file and helper.allowed_file(file.filename):
            extension = file.filename.rsplit('.' ,1)
            filename = secure_filename(file.filename)
            filename = helper.hash_filename(filename)+"."+extension[1]
            # saves file in file system
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = 'no_picture.jpg'
        newPlayer = Player(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            skill_level=request.form['skill_level'],
            picture=filename,
            summary=request.form['summary'],
            team_id=team_id,
            share_contact=request.form['share_contact'],
            created_on=datetime.datetime.strptime(strftime("%Y-%m-%d %H:%M:%S", localtime()), "%Y-%m-%d %H:%M:%S"),
            created_by=login_session['user_id'],
            is_active='1' if request.form['status'] == 'Active' else '0',
            is_delete='0',
            )
        session.add(newPlayer)
        session.commit()
        flash('New Player %s Successfully Created' % newPlayer.name)
        return redirect(url_for('showPlayers', team_id=team_id))
    else:
        skill_levels = ['Beginner', 'Intermediate', 'Advanced']
        return render_template('players/newplayer.html', skill_levels=skill_levels)


# Edit player details
@app.route('/team/<int:team_id>/player/<int:player_id>/edit', methods=["GET", "POST"])
def editPlayer(team_id, player_id):
    if 'username' not in login_session:
        return redirect('/login')
    player = session.query(Player).filter_by(team_id=team_id, is_delete='0', id=player_id).one()
    if player.created_by != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this player. Please create your own player in order to edit.');}</script><body onload='myFunction()''>"
    team = session.query(Team).filter_by(id=team_id).one()
    skill_levels = ['Beginner', 'Intermediate', 'Advanced']
    if request.method == "POST":
        player.name=request.form['name']
        player.email=request.form['email']
        player.phone=request.form['phone']
        player.skill_level=request.form['skill_level']
        player.summary=request.form['summary']
        player.is_active='1' if request.form['status'] == 'Active' else '0'
        player.share_contact=request.form['share_contact']

        if player.picture != request.files['picture']:
            file = request.files['picture']
            if file and helper.allowed_file(file.filename):
                extension = file.filename.rsplit('.' ,1)
                filename = secure_filename(file.filename)
                filename = helper.hash_filename(filename)+"."+extension[1]
                player.picture = filename
                # saves file in file system
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        session.add(player)
        session.commit()
        flash('Player %s Edited Successfully' % player.name)
        return redirect(url_for('showPlayers', team_id=team_id))
    return render_template('players/editplayer.html', skill_levels=skill_levels, player=player,team=team)


# Delete a player
@app.route('/team/<int:team_id>/player/<int:player_id>/delete', methods=["GET", "POST"])
def deletePlayer(team_id, player_id):
    if 'username' not in login_session:
        return redirect('/login')
    player = session.query(Player).filter_by(team_id=team_id, is_delete='0', id=player_id).one()
    if player.created_by != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this player. Please create your own player in order to delete.');}</script><body onload='myFunction()''>"
    team = session.query(Team).filter_by(id=team_id).one()
    if request.method == "POST":
        player.is_delete = '1'
        session.add(player)
        session.commit()
        flash('%s Deleted Successfully' % player.name)
        return redirect(url_for('showPlayers', team_id=team_id))
    else:
        return render_template('players/deleteplayer.html', player=player, team=team, team_id=team_id)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
