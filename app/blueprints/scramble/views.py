from manage import app
from . import scramble
from flask import Flask, render_template, request, session, redirect, url_for
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_login import current_user, login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from . import util
import random, pymysql, json, re, os, time, datetime
from ast import literal_eval

# app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database (Change database address when deploying)
engine = create_engine('mysql://root:kontravoid@localhost/project_italia')
db = engine.connect()


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

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult' LIMIT 20) SELECT ranking, first_name, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
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

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking WHERE user_id={user_id}"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking WHERE user_id={user_id}"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult') SELECT ranking, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking WHERE user_id={user_id}"
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
        query = f"SELECT game_id, game_content FROM scramble_approved WHERE game_type='{played_game_type}' and game_length<=7 order by rand() limit 1"
    elif game_difficulty == 'difficult':
        query = f"SELECT game_id, game_content FROM scramble_approved WHERE game_type='{played_game_type}' and game_length>=11 order by rand() limit 1"
    else:
        query = f"SELECT game_id, game_content FROM scramble_approved WHERE game_type='{played_game_type}' and game_length>=8 and game_length<=10 order by rand() limit 1"

    game = db.execute(query).fetchone()

    if game == None:
        return render_template('scramble/choosegames.html', message = "We do not have a game in that type & difficulty level yet. Please select another type/difficulty level, or create your own game submission.")

    game_id = game[0]
    game_content = literal_eval(game[1])

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
    elif played_game_type == 'video':
        full_video = ""
        return render_template('scramble/seevideogame.html', full_video = full_video)


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


@scramble.route('/videogame')
@login_required
def videogame():
    """Run video resequencing game"""

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
    for i in range(0, int(len(game_content)/2)):
        start = game_content.get(f'start{i}')
        end = game_content.get(f'end{i}')
        value = f"{start},{end}"
        cards.append(value)
        order[value] = i
    boxes = cards.copy()
    random.shuffle(cards)
    random.shuffle(cards)
    random.shuffle(cards)
    cardnum = len(cards)
    letters = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O']
    letters = letters[0:cardnum]
    return render_template("scramble/reorder.html", order=order, cards=cards, boxes=boxes, cardnum=cardnum, mode=mode, game_id=game_id, letters=letters, game_type="video")


@scramble.route('/submittime', methods=["POST"])
@login_required
def submittime():
    """Saves player's game time in scramble_scores table"""

    timer = int(request.form["time"])
    
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

    query = f"WITH game_ranking AS(SELECT game_epoch_time, user_id, first_name, game_difficulty, game_type, game_time, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores) SELECT ranking, first_name, game_difficulty, game_type, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking WHERE game_epoch_time={epoch_time} AND user_id='{user_id}'"
    ranking = db.execute(query).fetchone()

    return render_template("scramble/lastscore.html", ranking=ranking, game_type=played_game_type)


    

##---------------------------------------------------MANAGE GAMES (FOR ADMIN)-------------------------------------------------------##


@scramble.route('/managegames')
@login_required
def managegames():
    """Show full game database to administrator only"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.managesubmitted'))

    manage_title = "Game Database"

    query = "SELECT * FROM scramble_to_approve"
    to_approve = db.execute(query)
    query = "SELECT * FROM scramble_approved"
    approved = db.execute(query)
    return render_template('scramble/managegames.html', to_approve=to_approve, approved=approved, manage_title=manage_title)


@scramble.route('/adminpreview/<table>/<game_id>')
@login_required
def adminpreview(table, game_id):
    """Preview games in databases to administrator"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.managesubmitted'))

    query = f"SELECT game_content, game_type FROM {table} WHERE game_id={game_id}"
    game_content = literal_eval(db.execute(query).fetchone()[0])
    game_type = db.execute(query).fetchone()[1]

    if table=='scramble_to_approve':
        session['mode'] = 'adminapprove'
    elif table=='scramble_approved':
        session['mode'] = 'preview'

    session['game_id'] = game_id
    session['game_content'] = game_content

    if game_type == 'text':
        return redirect(url_for('scramble.textgame'))
    elif game_type == 'video':
        return redirect(url_for('scramble.videogame'))
        

@scramble.route('/adminapprove/<game_id>')
@login_required
def adminapprove(game_id):
    """Lets administrator approve user-submitted games (by moving a game from scramble_to_approve table to scramble_approved table in MySQL)"""

    if current_user.is_admin != 1:
        return redirect(url_for('scramble.index'))

    query = f"SELECT game_category FROM scramble_to_approve WHERE game_id={game_id}"
    category = db.execute(query).fetchone()[0]

    allcatquery, allcat = util.getCategories('scramble_approved')

    if category not in allcat:
        query = f"ALTER TABLE scramble_approved MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{category}')"
        db.execute(query)
    
    approved_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query = f"INSERT INTO scramble_approved(approved_time, game_id, user_id, first_name, user_email, submit_time, game_type, game_length, game_category, game_title, game_content) SELECT '{approved_time}', game_id, user_id, first_name, user_email, submit_time, game_type, game_length, game_category, game_title, game_content from scramble_to_approve WHERE game_id={game_id}"
    db.execute(query)
    query = f"DELETE FROM scramble_to_approve WHERE game_id={game_id}"
    db.execute(query)
    
    return redirect(url_for('scramble.managegames'))


@scramble.route('/admindiscard/<table>/<game_id>')
@login_required
def admindiscard(table, game_id):
    """Lets administrator delete games (from either scramble_to_approve or scramble_approved table)"""

    query = f"DELETE FROM {table} WHERE game_id={game_id}"
    db.execute(query)

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

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='easy') SELECT ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
    easy = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='medium') SELECT ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
    medium = db.execute(query)

    query = f"WITH game_ranking AS(SELECT *, RANK() OVER(ORDER BY game_time)ranking FROM scramble_scores WHERE game_type='{game_type}' AND game_difficulty='difficult') SELECT ranking, first_name, user_id, game_difficulty, game_type, game_id, submit_time, SEC_TO_TIME(game_time) AS game_time_sec from game_ranking"
    difficult = db.execute(query)
    
    return render_template('scramble/scores.html', game_type=game_type, easy=easy, medium=medium, difficult=difficult, score_title=score_title)


@scramble.route('/scorediscard/<score_id>/')
@login_required
def scorediscard(user_id, score_id, game_id):
    """Lets administrator remove game scores from database"""
    query = f"DELETE FROM scramble_scores WHERE score_id={score_id}"
    db.execute(query)

    return redirect(url_for('scramble.managescores'))


##---------------------------------------------------MANAGE GAMES (FOR PLAYERS)-------------------------------------------------------##

@scramble.route('/managesubmitted')
@login_required
def managesubmitted():
    """Show game database to administrator only"""

    manage_title = "My Submitted Games"
    user_id = int(current_user.id)

    query = f"SELECT * FROM scramble_to_approve WHERE user_id={user_id}"
    to_approve = db.execute(query)
    query = f"SELECT * FROM scramble_approved WHERE user_id={user_id}"
    approved = db.execute(query)

    return render_template('scramble/managegames.html', to_approve=to_approve, approved=approved, manage_title=manage_title)

@scramble.route('/userpreview/<table>/<game_id>')
@login_required
def userpreview(table, game_id):
    """Preview games in databases to administrator"""

    user_id = current_user.id

    query = f"SELECT game_content, user_id, game_type FROM {table} WHERE game_id={game_id}"

    if user_id != db.execute(query).fetchone()[1]:
        return redirect(url_for('scramble.index'))

    game_content = literal_eval(db.execute(query).fetchone()[0])
    session['game_content'] = game_content

    game_type = db.execute(query).fetchone()[2]

    if table=='scramble_to_approve':
        session['mode'] = 'usersubmitted'
    elif table=='scramble_approved':
        session['mode'] = 'preview'

    session['game_id'] = game_id

    if game_type == 'text':
        return redirect(url_for('scramble.textgame'))
    elif game_type == 'video':
        return redirect(url_for('scramble.videogame'))

##------------------------------------------------- CREATE GAME--------------------------------------------------------------------##

@scramble.route('/cancelcreate')
@login_required
def cancelcreate():
    """Let user cancel game creation, deletes autosaved game info from session"""

    if 'game_title' in session:
        session.pop('game_title', None)
        session.pop('game_type', None)
        session.pop('game_category', None)
        session.pop('allcatquery', None)
        session.pop('newcat', None)
        if 'game_content' in session:
            session.pop('game_content', None)
        if 'game_input' in session:
            session.pop('game_input', None)
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
        newcat = session.get('newcat')
        saved = {'game_title':game_title, 'game_type':game_type, 'game_category':game_category, 'newcat':newcat}
    else:
        saved = dict()

    allcatquery, allcat = util.getCategories('scramble_to_approve')

    session['allcatquery'] = allcatquery
    session['allcat'] = allcat
    session['saved'] = saved
    message=""
    return render_template("scramble/gameinfo.html", allcat=allcat, saved=saved, message=message)


@scramble.route('/create', methods=["GET", "POST"])
@login_required
def create():
    """Store form input to submit new game"""

    if 'game_type' in session:
        game_type = session.get('game_type')

    if 'allcat' in session:
        allcat = session.get('allcat')
        saved = session.get('saved')

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
        # Do not ask for username & password game is housed in larger website.
        # Instead get username & e-mail from session
        game_title = str(request.form.get("game_title"))
        game_type = str(request.form.get("game_type"))
        game_category = str(request.form.get("game_category"))
        newcat = ""

        #If 'Video' game type is selected, get YouTube link
        if game_type == 'video':
            youtubelink = str(request.form.get("youtubelink"))
            youtube = util.getVideoId(youtubelink)
            session['youtube'] = youtube

        # If 'Other' category is selected, save the string input into new category
        if game_category == "Other":
            game_category = str(request.form.get("new_category"))
            if game_category not in allcat:
                newcat = "other"
            else:
                message = "The category you entered already exists. Please select it from the dropdown menu."
                return render_template("scramble/gameinfo.html", allcat=allcat, saved=saved, message=message)
        
        # Store form input into session
        session['game_title'] = game_title
        session['game_type'] = game_type
        session['game_category'] = game_category
        session['newcat'] = newcat
        session['mode'] = 'createpreview'

    if game_type == 'text':
        return render_template("scramble/createtext1.html", game_content=game_content, game_input=game_input)
    if game_type == 'video':
        if youtube=='invalid':
            message = "The YouTube link you entered is invalid. Please make sure it follows this format: <i>https://www.youtube.com/<b>watch?v=</b>M7lc1UVf-VE</i>"
            return render_template("scramble/gameinfo.html", allcat=allcat, saved=saved, message=message)
        return render_template("scramble/createvideo1.html", game_content=game_content, game_input=game_input, youtube=youtube)


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
    return render_template("scramble/previewtext.html", game_content=game_content)


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

    return render_template("scramble/previewtext.html", game_content=game_content)

@scramble.route('/createvideo', methods=["POST"])
@login_required
def createvideo():
    """Store video start and end times entered into each card from multiple fields"""

    youtube = session.get('youtube')

    startend = dict(request.form.to_dict())
    game_input = "multifields"

    game_length = int(len(dict(startend))/2)

    game_content = dict()

    for i in range(gamelength):
        starttime = startend[f'start{i}']
        endtime = startend[f'end{i}']
        link = f"https://www.youtube-nocookie.com/embed/{youtube}?start={starttime}&end={endtime};autohide=1&controls=0"
        game_content[i] = link

    session['game_content'] = game_content
    session['game_length'] = game_length
    session['game_input'] = game_input
    session['youtube'] = youtube

    return render_template("scramble/previewvideo.html", game_content=game_content)


# Create New Game - Step5: save game into SQL database
@scramble.route('/save')
@login_required
def save():
    """Save game information into SQL table to be reviewed by administrator"""

    game_content = json.dumps(session.get('game_content'))
    user_id =  int(current_user.id)
    first_name = current_user.first_name
    user_email =  current_user.email
    submit_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    game_title = session.get('game_title')
    game_length = session.get('game_length')
    game_type = session.get('game_type')
    game_category = session.get('game_category')
    newcat = session.get('newcat')
    allcatquery = session.get('allcatquery')
    if newcat == "other":
        query = f"ALTER TABLE scramble_to_approve MODIFY COLUMN game_category {allcatquery[:len(allcatquery)-1]}, '{game_category}')"
        db.execute(query)
    query = "INSERT INTO scramble_to_approve(user_id, first_name, user_email, submit_time, game_title, game_length, game_type, game_category, game_content) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (user_id, first_name, user_email, submit_time, game_title, game_length, game_type, game_category, game_content)
    db.execute(query, val)

    # Remove any previous form input from session
    # Do not drop username & useremail from session if housed in larger website
    session.pop('game_title', None)
    session.pop('game_length', None)
    session.pop('game_type', None)
    session.pop('game_category', None)
    session.pop('allcatquery', None)
    session.pop('newcat', None)
    session.pop('game_content', None)
    session.pop('saved', None)
    if 'game_input' in session:
        session.pop('game_input', None)
    if 'mode' in session:
        session.pop('mode', None)

    return render_template("scramble/saved.html")

if __name__=='__main__':
    app.run(debug=True)