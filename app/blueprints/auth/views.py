from flask import render_template, request, redirect, url_for, flash
from . import auth
from .forms import RegisterForm, LoginForm
from app import db
from app.blueprints import main
from app.models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if form.validate_on_submit():
         
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is not None and check_password_hash(user.password, form.password.data):
            
            login_user(user, remember=form.remember_me.data)

            return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password')
        print("WRONG!")

    return render_template('auth/login.html', form=form)




@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if form.validate_on_submit():
        user = User()
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.password = generate_password_hash(form.password.data)
        user.is_admin = 0
        # user.gender = form.gender.data
        # user.date_of_birth = form.date_of_birth.data


        # Check if user e-mail is already registered
        exists = User.query.filter_by(email=form.email.data).scalar() is not None

        if exists:
            # flash('That e-mail address is already registered')
            return render_template('auth/reg_error.html', message="That e-mail address is already registered in this site.")
        else:
            db.session.add(user)
            db.session.commit()
            return render_template('auth/reg_confirm.html')

    print(form.errors)


    return render_template('auth/register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))