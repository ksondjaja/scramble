from flask_wtf import Form, FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField, RadioField, SelectField, BooleanField
from wtforms.validators import Required, Email, EqualTo

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[Required(), Email()])
    password = PasswordField(label='Password', validators=[Required()])
    remember_me = BooleanField(label='Remember Me')
    submit = SubmitField(label='Login')


class RegisterForm(FlaskForm):
    first_name = StringField(label='First Name', validators=[Required()])
    last_name = StringField(label='Last Name', validators=[Required()])
    email = StringField(label='Email', validators=[Required(), Email()])
    password = PasswordField(label='Password', validators=[Required()], _name='password')
    password_retype = PasswordField(label='Confirm Password', validators=[Required(), EqualTo('password')])
    # date_of_birth = DateField(label='Date of Birth')
    # gender = SelectField(label='Gender', choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], validators=[Required()])

    submit = SubmitField(label='Register')