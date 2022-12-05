from flask import redirect, url_for, g


def session_attached():
    if not g.get('session'):
        return redirect(url_for('dashboard.index'))