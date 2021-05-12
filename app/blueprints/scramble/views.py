from . import scramble
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.utils import secure_filename
from config import config
from shutil import copyfile
from . import util
import random, pymysql, json, re, os, time, datetime
from ast import literal_eval
from . import helpers

# app = Flask(__name__)

# Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

database_uri = config['default'].SQLALCHEMY_DATABASE_URI

# Set up database (Change database address when deploying)
engine = create_engine(database_uri)
db = engine.connect()

# Maximum file size for media upload (in Megabytes)
max_mb = 20

##----------------------------------------------------------HOME PAGE------------------------------------------------------------##
@scramble.route('/')
@login_required
def index():
    """Load home page"""

    if 'game_id' in session:
        session.pop('game_id', None)
    if 'epoch_time' in session:
        session.pop('epoch_time', None)
    if 'played_game_type' in session:
        session.pop('played_game_type', None)
    if 'game_difficulty' in session:
        session.pop('game_difficulty', None)

    return render_template('scramble/scrambleindex.html')

##----------------------------------------------------------VIEW SCORES------------------------------------------------------------##

@scramble.route('/seetimes/<game_type>')
@login_required
def seetimes(game_type):
    """Shows the user the top 20 high scores by difficulty level for scramble game, by game type"""

    if 'game_id' in session:
        session.pop('game_id', None)
    if 'epoch_time' in session:
        session.pop('epoch_time', None)
    if 'played_game_type' in session:
        session.pop('played_game_type', None)
    if 'game_difficulty' in session:
        session.pop('game_difficulty', None)

    score_title = "Top 20 High Scores"

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    difficult = db.execute(query)
    
    return render_template('scramble/scores.html', game_type=game_type, easy=easy, medium=medium, difficult=difficult, score_title=score_title)

@scramble.route('/seemytimes/<game_type>')
@login_required
def seemytimes(game_type):
    """Shows each player a history of all of their own scores"""

    if 'game_id' in session:
        session.pop('game_id', None)
    if 'epoch_time' in session:
        session.pop('epoch_time', None)
    if 'played_game_type' in session:
        session.pop('played_game_type', None)
    if 'game_difficulty' in session:
        session.pop('game_difficulty', None)

    score_title = "My Game Scores"
    user_id = int(current_user.id)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking WHERE user_id={user_id}"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking WHERE user_id={user_id}"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking WHERE user_id={user_id}"
    difficult = db.execute(query)
    
    return render_template('scramble/scores.html', game_type=game_type, easy=easy, medium=medium, difficult=difficult, score_title=score_title)

##----------------------------------------------------------PLAY GAME------------------------------------------------------------##

@scramble.route('/choosegames')
@login_required
def choosegames():
    """Select game to play"""

    if 'game_id' in session:
        session.pop('game_id', None)
    if 'epoch_time' in session:
        session.pop('epoch_time', None)
    if 'played_game_type' in session:
        session.pop('played_game_type', None)
    if 'game_difficulty' in session:
        session.pop('game_difficulty', None)

    return render_template('scramble/choosegames.html')

@scramble.route('/playgame', methods=["POST"])
@login_required
def playgame():
    """Retrieves game from scramble_apprvoed table"""

    played_game_type = request.form["played_game_type"]
    game_difficulty = request.form["game_difficulty"]

    if game_difficulty == 'easy':
        query = f"SELECT game_id, game_content, game_title, game_length FROM scramble_games WHERE is_approved=1 AND game_type='{played_game_type}' AND game_length<=7 ORDER BY RANDOM() LIMIT 1"
    elif game_difficulty == 'difficult':
        query = f"SELECT game_id, game_content, game_title, game_length FROM scramble_games WHERE is_approved=1 AND game_type='{played_game_type}' AND game_length>=11 ORDER BY RANDOM() LIMIT 1"
    else:
        query = f"SELECT game_id, game_content, game_title, game_length FROM scramble_games WHERE is_approved=1 AND game_type='{played_game_type}' AND game_length>=8 and game_length<=10 ORDER BY RANDOM() LIMIT 1"

    game = db.execute(query).fetchone()

    if game == None:
        return render_template('scramble/choosegames.html', message = "We do not have a game in that type & difficulty level yet. Please select another type/difficulty level, or create your own game submission.")

    game_id = game[0]
    game_content = literal_eval(game[1])
    game_title = game[2]
    game_length = game[3]

    session['mode'] = 'game'
    session['game_id'] = game_id
    session['game_content'] = game_content
    session['game_difficulty'] = game_difficulty
    session['played_game_type'] = played_game_type

    if played_game_type == 'text':

        full_text = ""

        for i in range(0, len(game_content)):
            value = game_content.get(f'{i}')
            full_text = full_text + value + " "

        return render_template('scramble/seetextgame.html', full_text = full_text)

    elif played_game_type in ['video','audio']:

        if played_game_type =='video':
            instruction = "Watch the full video"
        elif played_game_type == 'audio':
            instruction = "Listen to the full audio"

        start = game_content["0"].split(" ")
        end = game_content[f"{game_length-1}"].split(" ")
        full_media = f"{start[0]} {end[1]}"

        media_path = util.get_s3_object_path(f'uploaded_games/{game_title}')
        media_format = f'{played_game_type}/{game_title.split(".")[-1]}'
        
        session['media_path'] = media_path
        session['media_file_name'] = game_title
        session['media_format'] = media_format
        session['game_type'] = played_game_type

        return render_template('scramble/seemediagame.html', played_game_type=played_game_type, media_path = media_path, media_format=media_format, full_media = full_media, instruction=instruction)


@scramble.route('/textgame')
@login_required
def textgame():
    """Run text resequencing game"""

    first_name = current_user.first_name

    game_content = session.get('game_content')

    if 'game_id' in session:
        game_id = session.get('game_id')
    else:
        game_id = None

    if 'mode' in session:
        mode = session.get('mode')

    boxes = []
    cards = []
    order = dict()
    for i in range(0, len(game_content)):
        value = game_content.get(f'{i}')
        cards.append(value)
        order[value] = i
    boxes = cards.copy()
    random.shuffle(cards)
    random.shuffle(cards)
    random.shuffle(cards)
    cardnum = len(cards)
    return render_template("scramble/reorder.html", order=order, cards=cards, boxes=boxes, cardnum=cardnum, mode=mode, game_id=game_id, game_type="text", first_name=first_name)


@scramble.route('/mediagame')
@login_required
def mediagame():
    """Run video resequencing game"""

    first_name = current_user.first_name

    media_path = session.get('media_path')
    media_file_name = session.get('media_file_name')
    media_format = session.get('media_format')
    game_content = session.get('game_content')
    game_type = session.get('game_type')

    game_content = session.get('game_content')

    if 'game_id' in session:
        game_id = session.get('game_id')
    else:
        game_id = None

    if 'mode' in session:
        mode = session.get('mode')

    boxes = []
    cards = []
    order = dict()
    for i in range(0, len(game_content)):
        value = game_content.get(f'{i}')
        cards.append(value)
        order[value] = i

    boxes = cards.copy()
    random.shuffle(cards)
    random.shuffle(cards)
    random.shuffle(cards)
    cardnum = len(cards)

    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O']
    letters = letters[0:cardnum]

    return render_template("scramble/reorder.html", order=order, cards=cards, boxes=boxes, cardnum=cardnum, mode=mode, game_id=game_id, letters=letters, game_type=game_type, first_name = first_name, media_path=media_path, media_format=media_format)


@scramble.route('/submittime', methods=["POST"])
@login_required
def submittime():
    """Saves player's game time in scramble_scores table"""

    timer = int(request.form["time"])
    timer = datetime.timedelta(seconds=timer)
    
    if 'game_id' in session:
        game_id = session.get("game_id")
    
    user_id = int(current_user.id)
    first_name = current_user.first_name
    game_difficulty = session.get("game_difficulty")
    played_game_type = session.get("played_game_type")
    submit_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    epoch_time = int(time.time())
    session['epoch_time'] = epoch_time

    query = "INSERT INTO scramble_scores(game_epoch_time, user_id, first_name, game_difficulty, game_type, game_id, game_time, submit_time) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    val = (epoch_time, user_id, first_name, game_difficulty, played_game_type, game_id, timer, submit_time)
    db.execute(query, val)

    session.pop('game_content', None)
    session.pop('game_id', None)
    
    if 'media_path' in session:
        session.pop('media_path', None)
        session.pop('media_file_name', None)
        session.pop('media_format', None)

    return redirect(url_for('scramble.lastgamescore'))

@scramble.route('/lastgamescore')
@login_required
def lastgamescore():
    """Shows player their last game's time & ranking"""

    epoch_time = session.get('epoch_time')
    user_id = int(current_user.id)
    first_name = current_user.first_name
    game_difficulty = session.get("game_difficulty")
    played_game_type = session.get("played_game_type")

    query = f"WITH game_ranking AS(SELECT game_epoch_time, user_id, first_name, game_difficulty, game_type, game_time, RANK() OVER(ORDER BY game_time DESC)ranking FROM scramble_scores) SELECT ranking, first_name, game_difficulty, game_type, game_time from game_ranking WHERE game_epoch_time={epoch_time} AND user_id='{user_id}'"
    ranking = db.execute(query).fetchone()

    session.pop('played_game_type', None)
    session.pop('game_type', None)

    return render_template("scramble/lastscore.html", ranking=ranking, game_type=played_game_type)


    

##---------------------------------------------------MANAGE GAMES (FOR ADMIN)-------------------------------------------------------##


@scramble.route('/managegames')
@login_required
def managegames():
    """Show full game database to administrator only"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.managesubmitted'))

    manage_title = "Game Database"

    query = "SELECT * FROM scramble_games WHERE is_approved=0"
    to_approve = db.execute(query)
    query = "SELECT * FROM scramble_games WHERE is_approved=1"
    approved = db.execute(query)
    return render_template('scramble/managegames.html', to_approve=to_approve, approved=approved, manage_title=manage_title)


@scramble.route('/adminpreview/<table>/<game_id>')
@login_required
def adminpreview(table, game_id):
    """Preview games in databases to administrator"""

    if 'game_content' in session:
        session.pop('game_content', None)
    if 'game_id' in session:
        session.pop('game_id', None)
    if 'media_path' in session:
        session.pop('media_format', None)
    if 'media_type' in session:
        session.pop('media_type', None)

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.managesubmitted'))

    query = f"SELECT game_content, game_type, game_title FROM scramble_games WHERE is_approved={table} AND game_id={game_id}"
    game = db.execute(query).fetchone()
    game_content = literal_eval(game[0])
    game_type = game[1]
    game_title = game[2]

    if table=='0':
        session['mode'] = 'adminapprove'
    elif table=='1':
        session['mode'] = 'preview'


    if game_type in ['audio', 'video']:

        if table=='0':
            session['media_path'] = util.get_s3_object_path(f'temporary/{game_title}')
        elif table=='1':
            session['media_path'] = util.get_s3_object_path(f'uploaded_games/{game_title}')

        media_format = f'{game_type}/{game_title.split(".")[-1]}'

        session['media_file_name'] = game_title
        session['media_format'] = media_format
    

    session['game_id'] = game_id
    session['game_content'] = game_content
    session['game_type'] = game_type
    

    if game_type == 'text':
        return redirect(url_for('scramble.textgame'))
    elif game_type in ['video', 'audio']:
        return redirect(url_for('scramble.mediagame'))
        

@scramble.route('/adminapprove/<game_id>')
@login_required
def adminapprove(game_id):
    """Lets administrator approve user-submitted games (by changing is_approved from 0 to 1)"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.index'))

    query = f"SELECT game_category, game_type, game_title FROM scramble_games WHERE is_approved=0 AND game_id={game_id}"
    game_category = db.execute(query).fetchone()[0]
    game_type = db.execute(query).fetchone()[1]
    game_title = db.execute(query).fetchone()[2]

    # allcatquery, allcat = util.get_categories()

    # if game_category not in allcat:
    #     query = f"ALTER TABLE scramble_games MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{game_category}')"
    #     db.execute(query)
    
    approved_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query = f"UPDATE scramble_games SET is_approved=1, approved_time = '{approved_time}' WHERE game_id={game_id}"
    db.execute(query)
    

    if game_type in ['video', 'audio']:

        util.copy_to_s3_permanent_folder(game_title)
        util.delete_from_s3('temporary', game_title)
    
    return redirect(url_for('scramble.managegames'))


@scramble.route('/admindiscard/<table>/<game_id>')
@login_required
def admindiscard(table, game_id):
    """Lets administrator delete games (either approved or not yet approved)"""

    query = f"SELECT game_title, game_type FROM scramble_games WHERE is_approved={table} AND game_id={game_id}"
    game_info = db.execute(query).fetchone()
    game_title = game_info[0]
    game_type = game_info[1]

    query = f"DELETE FROM scramble_games WHERE is_approved={table} AND game_id={game_id}"
    db.execute(query)

    if game_type in ['video', 'audio']:

        # perm_dir = config['default'].UPLOAD_DIRECTORY
        # path = os.path.join(perm_dir, secure_filename(game_title))

        # os.remove(path)

        if table=='0':
            s3_folder = 'temporary'
        else:
            s3_folder = 'uploaded_games'

        util.delete_from_s3(s3_folder, game_title)


    return redirect(url_for('scramble.managegames'))

@scramble.route('/managescores/<game_type>')
@login_required
def managescores(game_type):
    """Lets administrator see and manage all game scores from database"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.seetimes'))

    if 'game_id' in session:
        session.pop('game_id', None)
    if 'epoch_time' in session:
        session.pop('epoch_time', None)
    if 'played_game_type' in session:
        session.pop('played_game_type', None)
    if 'game_difficulty' in session:
        session.pop('game_difficulty', None)

    score_title = "Manage Scores"

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy') SELECT score_id, ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium') SELECT score_id, ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult') SELECT score_id, ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, game_time from game_ranking"
    difficult = db.execute(query)
    
    return render_template('scramble/scores.html', game_type=game_type, easy=easy, medium=medium, difficult=difficult, score_title=score_title)


@scramble.route('/scorediscard/<score_id>/')
@login_required
def scorediscard(score_id):
    """Lets administrator remove game scores from database"""
    query = f"DELETE FROM scramble_scores WHERE score_id={score_id}"
    db.execute(query)

    return redirect(url_for('scramble.managescores', game_type='text'))


##---------------------------------------------------MANAGE GAMES (FOR PLAYERS)-------------------------------------------------------##

@scramble.route('/managesubmitted')
@login_required
def managesubmitted():
    """Let users view and manage their own submitted games"""

    manage_title = "My Submitted Games"
    user_id = int(current_user.id)

    query = f"SELECT * FROM scramble_games WHERE is_approved=0 AND user_id={user_id}"
    to_approve = db.execute(query)
    query = f"SELECT * FROM scramble_games WHERE is_approved=1 AND user_id={user_id}"
    approved = db.execute(query)

    return render_template('scramble/managegames.html', to_approve=to_approve, approved=approved, manage_title=manage_title)

@scramble.route('/userpreview/<table>/<game_id>')
@login_required
def userpreview(table, game_id):
    """Preview games in databases to the user that submitted them"""

    if 'game_content' in session:
        session.pop('game_content', None)
    if 'game_id' in session:
        session.pop('game_id', None)
    if 'media_path' in session:
        session.pop('media_format', None)
    if 'media_type' in session:
        session.pop('media_type', None)

    user_id = current_user.id    

    query = f"SELECT game_content, game_type, game_title, user_id FROM scramble_games WHERE is_approved={table} AND game_id={game_id}"
    game = db.execute(query).fetchone()
    game_content = literal_eval(game[0])
    game_type = game[1]
    game_title = game[2]
    game_user_id = game[3]

    if user_id != game_user_id:
        return redirect(url_for('scramble.index'))

    if table=='0':
        session['mode'] = 'usersubmitted'
    elif table=='1':
        session['mode'] = 'preview'


    if game_type in ['audio', 'video']:
        
        if table=='0':
            session['media_path'] = util.get_s3_object_path(f'temporary/{game_title}')
        elif table=='1':
            session['media_path'] = util.get_s3_object_path(f'uploaded_games/{game_title}')

        media_format = f'{game_type}/{game_title.split(".")[-1]}'

        session['media_file_name'] = game_title
        session['media_format'] = media_format
    

    session['game_id'] = game_id
    session['game_content'] = game_content
    session['game_type'] = game_type
    

    if game_type == 'text':
        return redirect(url_for('scramble.textgame'))
    elif game_type in ['video', 'audio']:
        return redirect(url_for('scramble.mediagame'))

##------------------------------------------------- CREATE GAME--------------------------------------------------------------------##

@scramble.route('/cancelcreate')
@login_required
def cancelcreate():
    """Let user cancel game creation, deletes autosaved game info from session"""

    if 'game_type' in session:
        game_type = session.get('game_type')
        
        if game_type in ['audio', 'video']:

            if 'game_title' in session:
                util.delete_from_s3('temporary', game_title)
                session.pop('game_title', None)

        session.pop('game_type', None)

    if 'game_content' in session:
        session.pop('game_content', None)
    if 'game_title' in session:
        session.pop('game_title', None)
    if 'game_length' in session:
        session.pop('game_length', None)
    if 'game_category' in session:
        session.pop('game_category', None)
    if 'newcat' in session:
        session.pop('newcat', None)
    if 'media_file_name' in session:
        session.pop('media_file_name', None)
    if 'media_format' in session:
        session.pop('media_format', None)
    if 'media_path' in session:
        session.pop('media_path', None)
    if 'media_temp_path' in session:
        session.pop('media_temp_path', None)
    if 'full_media' in session:
        session.pop('full_media', None)

    return redirect(url_for('scramble.index'))


@scramble.route('/gameinfo')
@login_required
def gameinfo():
    """Generate form to submit new game"""

    # Load form input values if in session
    if 'game_title' in session:
        game_title = session.get('game_title')
        game_type = session.get('game_type')
        game_category = session.get('game_category')
    else:
        game_title = ''
        game_type = ''
        game_category = ''

    allcat = util.get_categories()

    #session['allcatquery'] = allcatquery
    session['allcat'] = allcat
    message=''
    return render_template("scramble/gameinfo.html", allcat=allcat, game_title=game_title, game_type=game_type, game_category=game_category, message=message)


@scramble.route('/create', methods=["GET", "POST"])
@login_required
def create():
    """Store form input to submit new game"""

    if 'game_title' in session:
        game_title = session.get('game_title')
        game_type = session.get('game_type')
        game_category = session.get('game_category')

    if 'allcat' in session:
        allcat = session.get('allcat')

    # Load game content if in session
    if 'game_content' in session:
        game_content = session.get('game_content')
    else:
        game_content = dict()

    if 'game_input' in session:
        game_input = session.get('game_input')
    else:
        game_input = ""

    if request.method == 'POST':
        # Save form input into variables
        game_title = str(request.form.get("game_title"))
        game_type = str(request.form.get("game_type"))
        game_category = str(request.form.get("game_category"))
        newcat = ''

        #If 'Video' game type is selected, get YouTube link
        # if game_type == 'video':
        #     youtubelink = str(request.form.get("youtubelink"))
        #     youtube = util.getVideoId(youtubelink)
        #     session['youtube'] = youtube

        # If 'Other' category is selected, save the string input into new category
        if game_category == "Other":
            game_category = str(request.form.get("new_category"))
            if game_category not in allcat:
                newcat = "other"
            else:
                message = "The category you entered already exists. Please select it from the dropdown menu."
                return render_template("scramble/gameinfo.html", allcat=allcat, game_title=game_title, game_type=game_type, game_category=game_category, message=message)
        
        # Store form input into session
        session['game_title'] = game_title
        session['game_type'] = game_type
        session['game_category'] = game_category
        session['newcat'] = newcat
        session['mode'] = 'createpreview'

    if game_type == 'text':
        return render_template("scramble/createtext1.html", game_content=game_content, game_input=game_input)
    if game_type in ['video','audio']:
        return render_template("scramble/uploadmedia.html", max_mb=max_mb, game_type=game_type)
    
# if youtube=='invalid':
#     message = "The YouTube link you entered is invalid. Please make sure it follows this format: <i>https://www.youtube.com/<b>watch?v=</b>M7lc1UVf-VE</i>"
#     return render_template("scramble/gameinfo.html", allcat=allcat, saved=saved, message=message)
# return render_template("scramble/createvideo1.html", game_content=game_content, game_input=game_input, youtube=youtube)


@scramble.route('/createtext2a', methods=["POST"])
@login_required
def createtext2a():
    """Store values entered into each card from multiple fields"""

    game_content = request.form.to_dict()
    game_input = "multifields"

    game_length = len(dict(game_content))

    session['game_content'] = game_content
    session['game_length'] = game_length
    session['game_input'] = game_input

    return redirect(url_for('scramble.previewtext'))


@scramble.route('/createtext2b', methods=["POST"])
@login_required
def createtext2b():
    """Automatically cut paragraphs into sentences, and store each sentence into each card"""

    game_input = "paragraph"

    # Get text from textarea
    paragraph = str(request.form.get("inputparagraph"))

    # Remove extra whitespace
    paragraph = paragraph.strip()
    paragraph = re.sub("\s+", " ", paragraph)

    # Add each sentence ending with period, question mark, or exclamation mark as a dictionary item
    ## Figure out how to detect multiple punctuations in a row
    game_content = dict()
    sentence=""
    j=0
    for i in range(len(paragraph)):
        if (paragraph[i] in '.!?') or (i==(len(paragraph)-1)):
            sentence += paragraph[i]
            game_content.update({f'{j}': sentence})
            sentence = ""
            j += 1
        else:
            sentence += paragraph[i]

    game_length = len(game_content)

    if game_length<5 or game_length>15:
        return render_template("scramble/createtext1.html", game_content=game_content, game_input=game_input, message="Please enter between 5 and 15 sentences in the paragraph.")

    session['game_content'] = game_content
    session['game_length'] = game_length
    session['game_input'] = game_input

    return redirect(url_for('scramble.previewtext'))


@scramble.route('/previewtext', methods=['GET'])
@login_required
def previewtext():
    """Preview entered text content during game creation"""

    game_content = session.get('game_content')

    return render_template("scramble/previewtext.html", game_content=game_content)


# Uploads file to tmp directory 
@scramble.route('/uploadtmp', methods=['POST'])
@login_required
def uploadtmp():
    """Upload media file to temporary folder to create video or audio game"""

    game_type = session.get('game_type')

    game_title = session.get('game_title')
    game_title = game_title.replace(" ", "_")

    upload_time = int(datetime.datetime.now().timestamp())

    #tmp_dir = config['default'].UPLOAD_DIRECTORY_TMP
    
    if request.files:

        uploaded_file = request.files['file-media']
        size = len(uploaded_file.read())
        uploaded_file.seek(0)

        file_name = uploaded_file.filename.split('.')
        media_file_name = f'{game_title}_{upload_time}.{file_name[-1]}'
        extension = file_name[-1]


        if game_type =='video':
            message = f"Please select a .mp4 video file sized under {max_mb}MB"
            
            if (size > max_mb*1024*1024) or (file_name[-1] not in ["mp4"]):
                return render_template("scramble/createmedia.html", message=message, extension=extension, size=size)
        elif game_type == 'audio':
            message = f"Please select a .mp3 or .wav audio file sized under {max_mb}MB"
            
            if (size > max_mb*1024*1024) or (file_name[-1] not in ["mp3", "wav"]):
                return render_template("scramble/createmedia.html", message=message, extension=extension, size=size)
        

        if uploaded_file.filename != '':
            util.upload_file_to_s3(uploaded_file, f'temporary/{media_file_name}')
            #path = os.path.join(tmp_dir, secure_filename(media_file_name))
            #uploaded_file.save(path)
    
        media_format = f"{game_type}/{file_name[-1]}"

        session['media_file_name'] = media_file_name
        session['media_format'] = media_format

        return redirect(url_for('scramble.createmedia'))


@scramble.route('/createmedia', methods=['GET'])
@login_required
def createmedia():
    """Create audio or video game after file upload"""

    if 'game_content' in session:
        game_content = session.get('game_content')
    else:
        game_content = dict()

    game_input = "multifields"

    game_type = session.get('game_type')
    media_file_name = session.get('media_file_name')
    media_format = session.get('media_format')

    media_temp_path = util.get_s3_object_path(f'temporary/{media_file_name}')

    session['media_temp_path'] = media_temp_path

    return render_template("scramble/createmedia2.html", media_temp_path=media_temp_path, media_format=media_format, game_content=game_content, game_input=game_input, game_type=game_type)


@scramble.route('/previewmedia', methods=["POST"])
@login_required
def previewmedia():
    """Store video start and end times entered into each card from multiple fields"""

    game_content = dict()

    startend = dict(request.form.to_dict())

    game_length = int(len(dict(startend))/2)

    full_media = ""

    for i in range(game_length):
        starttime = startend[f'start{i}']
        endtime = startend[f'end{i}']
        game_content[i] = f"{starttime} {endtime}"

        if i==0:
            full_media = full_media + f"{starttime} "
        
        if i==(game_length-1):
            full_media = full_media + f"{endtime}"
    

    session['game_content'] = game_content
    session['game_length'] = game_length
    session['full_media'] = full_media

    return redirect(url_for('scramble.previewmedia2'))


@scramble.route('/previewmedia2', methods=["GET"])
@login_required
def previewmedia2():
    """Preview game content for audio or video game"""

    media_temp_path = session.get('media_temp_path')
    media_file_name = session.get('media_file_name')
    media_format = session.get('media_format')
    game_content = session.get('game_content')
    full_media = session.get('full_media')
    game_type = session.get('game_type')

    session['media_path'] = media_temp_path

    return render_template("scramble/previewmedia.html", game_type=game_type, game_content=game_content, media_temp_path=media_temp_path, media_format=media_format, full_media=full_media)


# @scramble.route('/savemedia', methods=['GET'])
# @login_required
# def savemedia():
#     """Save audio or video game file by moving file from temporary to permanent folder"""

#     game_title = session.get('media_file_name')

#     tmp_dir = config['default'].UPLOAD_DIRECTORY_TMP
#     perm_dir = config['default'].UPLOAD_DIRECTORY

#     src = os.path.join(tmp_dir, secure_filename(game_title))
#     dst = os.path.join(perm_dir, secure_filename(game_title))

#     copyfile(src, dst)



#     session['game_title'] = game_title
    
#     return redirect(url_for('scramble.save'))


# Create New Game - Step5: save game into SQL database
@scramble.route('/save')
@login_required
def save():
    """Save game information into SQL table to be reviewed by administrator"""

    game_content = session.get('game_content')
    game_content_json = json.dumps(game_content)
    user_id =  int(current_user.id)
    first_name = current_user.first_name
    user_email =  current_user.email
    submit_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    game_title = session.get('game_title')
    game_length = session.get('game_length')
    game_type = session.get('game_type')
    game_category = session.get('game_category')
    newcat = session.get('newcat')
    
    if game_type in ['audio', 'video']:
        media_file_name = session.get('media_file_name')

    #allcatquery = session.get('allcatquery')
    # if newcat == "other":
    #     query = f"ALTER TABLE scramble_games MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{game_category}')"
    #     db.execute(query)
    
    query = "INSERT INTO scramble_games(user_id, first_name, user_email, submit_time, game_title, game_length, game_type, game_category, game_content) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
    if game_type == 'text':
        val = (user_id, first_name, user_email, submit_time, game_title, game_length, game_type, game_category, game_content_json)
    else:
        val = (user_id, first_name, user_email, submit_time, media_file_name, game_length, game_type, game_category, game_content_json)
    
    db.execute(query, val)

    # Remove any previous form input from session
    session.pop('game_content', None)
    session.pop('game_title', None)
    session.pop('game_length', None)
    session.pop('game_type', None)
    session.pop('game_category', None)
    session.pop('newcat', None)

    if 'media_file_name' in session:
        session.pop('media_file_name', None)
    if 'media_format' in session:
        session.pop('media_format', None)
    if 'media_path' in session:
        session.pop('media_path', None)
    if 'media_temp_path' in session:
        session.pop('media_temp_path', None)
    if 'full_media' in session:
        session.pop('full_media', None)

    return render_template("scramble/saved.html")

if __name__=='__main__':
    app.run(debug=True)