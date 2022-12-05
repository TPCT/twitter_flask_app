from flask import render_template, redirect, url_for, current_app
from flask_login import login_user, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from Forms.auth.LoginForm import LoginForm
from Models.UserModel import UserModel
from config import threads_pool
db = SQLAlchemy()


def index():
    authenticated = True

    if current_user.is_authenticated:
        if not threads_pool.get(current_user.id):
            threads_pool[current_user.id] = {}
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = UserModel.query.filter_by(username=form.username.data).first()
        if user and user.verifyPassword(form.password.data):
            login_user(user, remember=True)
            if not threads_pool.get(current_user.id):
                threads_pool[current_user.id] = {}
            return redirect(url_for('dashboard.index'))
        authenticated = False

    return render_template('Auth/login.html', title='Login', form=form
                           , authenticated=authenticated)


def logout():
    logout_user()
    return redirect("/")


def install():
    with current_app.app_context():
        user = UserModel.query.filter_by(username='admin').first()
        if not user:
            user = UserModel(username='admin', password='admin123', is_admin=True)
            db.session.add(user)
            db.session.commit()

    return "The App has been created successfully"
