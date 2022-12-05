import os
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from threading import Event
from flask_executor import Executor


SECRET_KEY = os.urandom(32)
basedir = os.path.abspath(os.path.dirname(__file__))
DEBUG = True

SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root@127.0.0.1/twitter_app_v4?charset=utf8mb4"
SQLALCHEMY_POOL_SIZE = 100000
SQLALCHEMY_POOL_RECYCLE = 10000
SQLALCHEMY_POOL_TIMEOUT = 20
SQLALCHEMY_TRACK_MODIFICATIONS = False
SESSION_TYPE = 'filesystem'
SESSION_PERMANENT = True
PRESERVE_CONTEXT_ON_EXCEPTION = False
EXECUTOR_TYPE = 'process'
UPLOAD_FOLDER = "/static/uploads"

threads_count = 0
max_threads_count = 20
free_threads_pool_event = Event()
threads_pool = {}
login = LoginManager()
db = SQLAlchemy(session_options={"expire_on_commit": False})
executor = Executor()