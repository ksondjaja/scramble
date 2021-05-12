'''
Contains the User model

'''
from app import db, login_manager
from flask_login import UserMixin

class User(db.Model, UserMixin):
    '''

    The User database model

    '''
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(128))
    # date_of_birth = db.Column(db.Date)
    # gender = db.Column(db.String(64))
    is_admin = db.Column(db.Integer)
    
    # All the MCQ quizzes created by this user
    mcq_quizzes = db.relationship('MCQuiz', backref='user', passive_deletes=True)
    # All the MCQ quizzes done by this user
    mcq_answersets = db.relationship('MCQAnswerSet', backref='user', passive_deletes=True)
    
    # All the Video Scramble Quizzes created by this user
    # video_scramble_quizzes = db.relationship('VideoScramble', backref='user', passive_deletes=True)
    



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))