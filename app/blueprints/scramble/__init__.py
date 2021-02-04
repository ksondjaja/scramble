import pymysql
pymysql.install_as_MySQLdb()

from flask import Blueprint

scramble = Blueprint('scramble', __name__, url_prefix='/scramble')

from . import views