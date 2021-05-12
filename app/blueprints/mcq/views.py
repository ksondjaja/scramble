from flask import render_template, request,redirect, jsonify, get_template_attribute, url_for
from flask_login import login_required, current_user
from . import mcq
from app import db
from app.models.mcq import MCQOption, MCQQuestion, MCQuiz, MCQAnswer, MCQAnswerSet
import datetime

@mcq.route('/')
def index():

    quizzes = MCQuiz.query.all()

    return render_template('mcq/index.html', quizzes=quizzes)


@mcq.route('/quiz/<id>', methods=['GET', 'POST'])
def quiz(id):


    if request.method == 'POST':

        answerset = MCQAnswerSet()
        answerset.quiz_id = id
        answerset.seconds_taken = request.json['time_taken']

        # If the user is logged in, set the user to the logged in user
        #otherwise leave it null
        if current_user.is_authenticated:
            answerset.user = current_user 


        total = len(MCQuiz.query.filter_by(id=id).first().questions)
        
        correct = 0

        for json_answer in request.json['answers']:
            answer = MCQAnswer()
            answer.option_id =  json_answer
            
            # If this chosen option is correct, then add to the correct
            if(MCQOption.query.filter_by(id=json_answer).first().is_correct):
                correct += 1

            answerset.answers.append(answer)


        answerset.score = correct / total;

        db.session.add(answerset)
        db.session.commit()
        

 
        return jsonify({"redirect": url_for('mcq.leaderboard', id=id)})

    else:
        quiz = MCQuiz.query.filter_by(id=id).first()
        return render_template('mcq/quiz.html', quiz=quiz)


@mcq.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    
    if request.method == 'POST':
        
        

        quiz = MCQuiz()
        quiz.title = request.json['title']
        quiz.description = request.json['description']
        quiz.user = current_user
        quiz.is_approved = False
        
        for json_question in request.json['questions']:
            question = MCQQuestion()
            question.title = json_question['title']
            question.category = json_question['category']
            question.content = json_question['content']
            
            for json_option in json_question['options']:
                option = MCQOption()
                option.content = json_option['content']
                option.is_correct = json_option['is_correct']
                
                question.options.append(option)

            quiz.questions.append(question)
        
        db.session.add(quiz)
        db.session.commit()


        return jsonify({"redirect": url_for('mcq.index')})

    else:
    
        return render_template('mcq/create.html')

@mcq.route('/approve-quiz/<id>', methods=['POST'])
@login_required
def approve_quiz(id):

    quiz = MCQuiz.query.filter_by(id=id).first()
    quiz.is_approved = True
    db.session.add(quiz)
    db.session.commit()

    render_card = get_template_attribute('/macros/_render_quiz_cards.html', 'render_quiz_card')

    html = render_card(quiz)
    return jsonify({'html': html})

 

@mcq.route('/leader/<id>')
def leaderboard(id):

    quiz = MCQuiz.query.filter_by(id=id).first()

    top_all = []

    for answerset in quiz.answersets.order_by(MCQAnswerSet.score.desc(), MCQAnswerSet.seconds_taken.asc()).limit(10).all():
        if(answerset.user):
            name = str(answerset.user.first_name) + " " + str(answerset.user.last_name)
        else:
            name = "Guest"

        score = str(round(answerset.score * 100,2) ) + "%" 
        time_taken = str(datetime.timedelta(seconds=answerset.seconds_taken))
        top_all.append({"name": name, "score": score, "time_taken": time_taken})
    
    
    top_user = []

    if current_user.is_authenticated:
        name = current_user.first_name + " " + current_user.last_name
        for answerset in quiz.answersets.filter_by(
                                                user_id=current_user.id
                                                ).order_by(
                                                MCQAnswerSet.score.desc(), 
                                                MCQAnswerSet.seconds_taken.asc()
                                                ).limit(10).all():
            
            score = str(round(answerset.score * 100,2) ) + "%" 
            time_taken = str(datetime.timedelta(seconds=answerset.seconds_taken))
            top_user.append({"name": name, "score": score, "time_taken": time_taken})


    return render_template('/mcq/leader.html', top_all=top_all, top_user =top_user )
