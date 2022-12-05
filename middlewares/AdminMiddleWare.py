from flask_login import current_user
from flask import redirect, url_for


def is_admin():
    if not current_user.is_admin:
        return redirect(url_for('dashboard.index'))