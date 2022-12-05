from flask import Flask, g
from flask_migrate import Migrate

import routes
from flask_session import Session
from flask_login import current_user

from config import *
from Models import *
from routes import *

from middlewares.AuthenticationMiddleWare import is_authenticated
from middlewares.AdminMiddleWare import is_admin
from middlewares.SessionMiddleWare import session_attached
from Database.DatabaseWorker import DatabaseThread

app = Flask(__name__)
app.config.from_object('config')

Session(app)
migration = Migrate(app, db)
login.init_app(app)
db.init_app(app)
executor.init_app(app)

with app.app_context():
    databaseThread = DatabaseThread()
    databaseThread.start()

for blueprint in routes.blueprints:
    if blueprint in routes.authentication_required:
        blueprint.before_request(is_authenticated)

    if blueprint in routes.admin_required:
        blueprint.before_request(is_admin)

    if blueprint in routes.session_required:
        blueprint.before_request(session_attached)

    app.register_blueprint(blueprint, url_prefix='/' if blueprint == AuthBluePrint else f'/{blueprint.name}')


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.flush()
    db.session.commit()
    db.session.remove()


@app.before_request
def initRequest(*args, **kwargs):
    if current_user and current_user.is_authenticated:
        g.setdefault('session', db.session.query(SessionModel).filter_by(user_id=current_user.id, selected=True).first())


@app.context_processor
def set_global_html_values():
    if current_user and current_user.is_authenticated:
        for session in current_user.sessions:
            if session.active:
                threads = threads_pool.get(current_user.id, {}).get(session.id, {})
                session.active = any([thread.is_alive() for class_name, thread in threads.items()])
                db.session.commit()

        current_session = g.get('session')
        sessions = db.session.query(SessionModel).filter_by(user_id=current_user.id).all()
        return {
            'current_session': current_session,
            'sessions': sessions,
            'is_admin': current_user.is_admin,
            'active': current_session.id in threads_pool.get(current_user.id, {}) if current_session else False
        }

    return {}


if __name__ == "__main__":
    app.run(threaded=True, port=8081, host='0.0.0.0', debug=True)