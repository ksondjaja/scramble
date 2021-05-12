from flask import Blueprint

exam = Blueprint('exam', __name__, url_prefix='/exam')

from . import views
