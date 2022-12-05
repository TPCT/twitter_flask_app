from flask import render_template, redirect, url_for, current_app
from Forms.dashboard.users.StoreForm import StoreForm
from Models.UserModel import UserModel
from Database.DatabaseWorker import DatabaseThread
from flask import request, flash
from config import db
from shutil import rmtree


def index():
    users = list(enumerate(db.session.query(UserModel).filter(UserModel.id != 1).all()))
    return render_template('Dashboard/Users.html',
                           title='Users',
                           users=users,
                           users_store_form=StoreForm())


def store():
    users_store_form = StoreForm()
    message = {'type': 'danger', 'text': "User hasn't created."}
    users_store_form.process(formdata=request.form)
    if users_store_form.validate_on_submit():
        user = UserModel.query.filter_by(username=users_store_form.username.data).first()
        if not user:
            user = UserModel(username=users_store_form.username.data,
                             password=users_store_form.password.data,
                             is_admin=users_store_form.is_admin.data)
            db.session.add(user)
            db.session.commit()
            message = {'type': 'success', 'text': 'User has been created'}

    flash(message)
    return redirect(url_for('users.index'))


def delete(account_id):
    user = UserModel.query.filter_by(id=account_id).first()
    sessions = user.sessions
    storage = user.storage

    for session in sessions.all():
        session.delete()

    storage.delete(synchronize_session='fetch')
    message = {'type': 'success', 'text': 'User has been deleted'}
    flash(message)
    return redirect(url_for('users.index'))