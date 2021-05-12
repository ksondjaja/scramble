from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Declare the extensions 

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = 'auth.login'

def create_app(config_name):
    '''

    Creates the flask application, initializes the extensions,
    and registers all the associated blueprints

    '''

    # Create the application
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)


    # Load Models - Must be before db.init_app  
    from .models.user import User
    from .models.mcq import MCQuiz, MCQQuestion, MCQOption
    
    # Initialize the extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from .blueprints.main import main as main_blueprint
    from .blueprints.auth import auth as auth_blueprint
    from .blueprints.mcq import mcq as mcq_blueprint
    from .blueprints.exam import exam as exam_blueprint
    from .blueprints.scramble import scramble as scramble_blueprint


    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(mcq_blueprint)
    app.register_blueprint(exam_blueprint)
    app.register_blueprint(scramble_blueprint)

    return app


