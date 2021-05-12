'''
Contains models relating to Scramble game

'''
from app import db
from app.models.user import User
import datetime, enum

class GameType(enum.Enum):
    '''
    Type of game content
    '''
    text = 1
    video = 2
    audio = 3

class GameDifficulty(enum.Enum):
    '''
    Level of game difficulty, based on number of cards
    5 to 7 cards --> easy
    8 to 10 cards --> medium
    11 to 15 cards --> difficult
    '''
    easy = 1
    medium = 2
    difficult = 3

class ScrambleToApprove(db.Model):
    '''
    For user-submitted games that are not yet approved
    '''
    __tablename__ = 'scramble_to_approve'
    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    first_name = db.Column(db.String(64), db.ForeignKey('users.first_name', ondelete='CASCADE'))
    user_email = db.Column(db.String(120), db.ForeignKey('users.email', ondelete='CASCADE'))
    submit_time = db.Column(db.DateTime, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    game_type = db.Column(db.Enum(GameType))
    game_length = db.Column(db.Integer)
    game_category = db.Column(db.String(64))
    game_title = db.Column(db.String(255))
    game_content = db.Column(db.Text)

class ScrambleApproved(db.Model):
    '''
    For games that are already approved by administrator and playable by all users
    '''
    __tablename__ = 'scramble_approved'
    game_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    first_name = db.Column(db.String(64), db.ForeignKey('users.first_name', ondelete='CASCADE'))
    user_email = db.Column(db.String(120), db.ForeignKey('users.email', ondelete='CASCADE'))
    submit_time = db.Column(db.DateTime)
    game_type = db.Column(db.Enum(GameType))
    game_length = db.Column(db.Integer)
    game_category = db.Column(db.String(64))
    game_title = db.Column(db.String(255))
    game_content = db.Column(db.Text)

    scores = db.relationship('ScrambleScores', backref='approved')

class ScrambleScores(db.Model):
    '''
    All game scores (the time it takes for a user to complete a game on play mode)
    '''
    __tablename__ = 'scramble_scores'
    score_id = db.Column(db.Integer, primary_key=True)
    game_epoch_time = db.Column(db.BigInteger)
    game_time = db.Column(db.Time)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    first_name = db.Column(db.String(64), db.ForeignKey('users.first_name', ondelete='CASCADE'))
    game_difficulty = db.Column(db.Enum(GameDifficulty))
    game_type = db.Column(db.Enum(GameType))
    game_id = db.Column(db.Integer, db.ForeignKey('scramble_approved.game_id', ondelete='CASCADE'))
    submit_time = db.Column(db.DateTime, default=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))