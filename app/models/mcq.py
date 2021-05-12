'''
Contains models relating to an MCQ quiz

'''
from app import db
from app.models.user import User

class MCQuiz(db.Model):
    '''

    Represents a multiple choice quiz

    '''
    __tablename__ = 'mcq_quizzes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    description = db.Column(db.String(200))
    is_approved = db.Column(db.Boolean())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    
    questions = db.relationship('MCQQuestion', backref='quiz', passive_deletes=True)
    answersets = db.relationship('MCQAnswerSet', backref='quiz', passive_deletes=True, lazy='dynamic')

    def __str__(self):

        s = 'Title: ' + str(self.title) + '\n'
        s += 'is_approved' + str(self.is_approved) + '\n'
        s += 'questions: \n' 
        
        for question in self.questions:
            s += str(question)
        
        return s

class MCQQuestion(db.Model):
    '''

    Represents a single question for a quiz

    '''
    __tablename__ = 'mcq_questions'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    category = db.Column(db.String(100))
    content = db.Column(db.String(400))
    quiz_id = db.Column(db.Integer, db.ForeignKey('mcq_quizzes.id', ondelete='CASCADE'))

    options = db.relationship('MCQOption', backref='question', passive_deletes=True)


    def __str__(self):


        s = 'Question: ' + str(self.title) + '\n'
        s += 'Content: ' + str(self.content) + '\n'
        s += 'Cateogry: ' + str(self.category) + '\n'
        
        s += 'Options: \n';

        for option in self.options:
            s += str(option)
        

        return s




class MCQOption(db.Model):
    '''
    Represents a single option for a single question
    '''
    __tablename__ = 'mcq_options'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(400))
    question_id = db.Column(db.Integer, db.ForeignKey('mcq_questions.id', ondelete='CASCADE'))
    is_correct = db.Column(db.Boolean)

    # All the instances of where this option was selected when asked its question
    selections = db.relationship('MCQAnswer', backref='option', passive_deletes=True)

    def __str__(self):

        s = 'Option: \n'
        s += 'Content: ' + str(self.content) + '\n'
        s += 'is_correct: ' +  str(self.is_correct) + '\n'

        return s



class MCQAnswerSet(db.Model):
    '''
    Represents a single answer set made by a user to a quiz
    '''
    __tablename__ = 'mcq_answersets'
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('mcq_quizzes.id', ondelete='CASCADE'))
    seconds_taken = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    score = db.Column(db.Float)
    answers = db.relationship('MCQAnswer', backref='answerset', passive_deletes=True)

class MCQAnswer(db.Model):
    '''
    Represents a single answer made to a single answer set
    '''
    __tablename__ = 'mcq_answers'
    id = db.Column(db.Integer, primary_key=True)
    answerset_id = db.Column(db.Integer, db.ForeignKey('mcq_answersets.id', ondelete='CASCADE'))
    option_id = db.Column(db.Integer, db.ForeignKey('mcq_options.id', ondelete='CASCADE'))

