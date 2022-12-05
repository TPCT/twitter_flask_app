from flask import render_template
from Forms.dashboard.session.StoreForm import StoreForm as SessionStoreForm
from Forms.dashboard.settings.StoreForm import StoreForm as SettingsStoreForm
from Models.AccountModel import AccountModel
from Constants.AccountTypes import AccountTypes


def index():
    session_form = SessionStoreForm()
    settings_form = SettingsStoreForm()
    return render_template('Dashboard/Dashboard.html',
                           model=AccountModel,
                           ACCOUNT_TYPES=AccountTypes.getAllPermissionsNames([AccountTypes.checker]),
                           session_form=session_form,
                           settings_form=settings_form,
                           title="Dashboard")
