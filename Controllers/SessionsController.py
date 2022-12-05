from flask import redirect, url_for, request, flash, g
from flask_login import current_user
from Forms.dashboard.session.StoreForm import StoreForm
from Models.SessionModel import SessionModel
from config import db, threads_pool


def store():
    session_store_form = StoreForm()
    message = {'type': 'danger', 'text': "Session hasn't created."}
    session_store_form.process(formdata=request.form)
    if session_store_form.validate_on_submit():
        session = SessionModel.query.filter_by(name=session_store_form.name.data).first()
        if not session:
            session = SessionModel(user_id=current_user.id, name=session_store_form.name.data)
            session.save()

            if not threads_pool.get(current_user.id):
                threads_pool[current_user.id] = {}

            if not threads_pool.get(current_user.id, {}).get(session.id):
                threads_pool[current_user.id][session.id] = {}

            message = {'type': 'success', 'text': 'Session has been created'}
        else:
            message['text'] = 'Session is already exists'
    flash(message)
    return redirect(url_for('dashboard.index'))


def select(session_id):
    message = {'type': 'danger', 'text': "Session hasn't selected."}
    previous_session = g.get('session')
    SessionModel.deactivate(previous_session)
    current_session = SessionModel.activate(session_id)
    if current_session:
        g.setdefault('session', current_session)
        message = {'type': 'success', 'text': 'Session has been selected'}
    flash(message)
    return redirect(url_for('dashboard.index'))


def delete(session_id):
    SessionModel.query.filter_by(id=session_id).first().delete()
    message = {'type': 'success', 'text': 'Session has been deleted'}
    flash(message)
    return redirect(url_for('dashboard.index'))
