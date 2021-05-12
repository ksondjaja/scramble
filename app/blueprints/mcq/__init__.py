from flask import Blueprint

mcq = Blueprint('mcq', __name__, url_prefix='/mcq')

from . import views
