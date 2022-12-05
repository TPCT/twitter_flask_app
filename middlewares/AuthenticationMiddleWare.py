from flask_login import current_user
from flask import redirect, url_for


def is_authenticated():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.index'))