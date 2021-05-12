from flask import render_template
from . import exam

@exam.route('/')
def index():
    return render_template('exam/index.html')


@exam.route('/create')
def create():
    return render_template('exam/create.html')