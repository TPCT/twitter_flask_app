from flask import redirect, url_for, flash
from flask_login import current_user
from config import threads_pool
from Models.SessionModel import SessionModel
from Database.DatabaseWorker import DatabaseThread


def store(session_id):
    message = {'type': 'danger', 'text': "Process hasn't started."}
    session = current_user.sessions.filter_by(id=session_id).first()
    if not session:
        message['text'] = 'Please select session to start'
        flash(message)
        return redirect(url_for('dashboard.index'))

    if session.active:
        message = {'type': 'success', 'text': 'Process is already active'}
        flash(message)
        return redirect(url_for('dashboard.index'))

    threads = threads_pool.get(current_user.id, {}).get(session_id, {})
    try:
        for class_name, thread in threads.items():
            if not thread.completed and not thread.is_alive():
                thread.start()
                DatabaseThread.update(SessionModel, id=session_id, active=True, completed=False)
    except Exception as e:
        pass

    message = {'type': 'success', 'text': "Process has started."}
    flash(message)
    return redirect(url_for('dashboard.index'))


def delete(session_id):
    message = {'type': 'danger', 'text': "Process hasn't terminated."}
    session = current_user.sessions.filter_by(id=session_id).first()

    if not session:
        message['text'] = "Can't terminate process without session"
        flash(message)
        return redirect(url_for('dashboard.index'))

    if not session.active:
        message = {'type': 'success', 'text': 'Process is already terminated'}
        flash(message)
        return redirect(url_for('dashboard.index'))

    threads = threads_pool.get(current_user.id, {}).get(session_id, {}).copy()

    for class_name, thread in threads.items():
        thread.terminate()

    if not (session.active or session.completed):
        DatabaseThread.update(SessionModel, id=session_id, active=False, completed=False)

    message = {'type': 'success', 'text': "Process has been terminated."}
    flash(message)
    return redirect(url_for('dashboard.index'))
