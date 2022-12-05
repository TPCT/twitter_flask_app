from Forms.checker.StoreForm import StoreForm as AccountStoreForm
from Workers.CheckerWorker import CheckerWorker
from Database.DatabaseWorker import DatabaseThread
from Models.AccountModel import AccountModel
from Models.ProxyModel import ProxyModel
from flask import redirect, url_for, flash, current_app, Response, render_template, g, request
from flask_login import current_user
from config import db
from Constants.AccountTypes import AccountTypes
from Constants.ProxyTypes import ProxyTypes


def index():
    db.session.flush()
    current_session = g.get('session')
    accounts_store_form = AccountStoreForm()
    active_accounts = list(enumerate(AccountModel.getMany(current_session.id, [AccountTypes.checker],
                                                          {'active': True})))
    suspended_accounts = list(enumerate(AccountModel.getMany(current_session.id, [AccountTypes.checker],
                                                             {'suspended': True})))
    restricted_accounts = list(enumerate(AccountModel.getMany(current_session.id, [AccountTypes.checker],
                                                              {'restricted': True})))
    return render_template('Dashboard/Checker.html',
                           accounts_form=accounts_store_form,
                           active_accounts=active_accounts,
                           suspended_accounts=suspended_accounts,
                           restricted_accounts=restricted_accounts,
                           accounts_counters={
                               'Active': len(active_accounts),
                               'Suspended': len(suspended_accounts),
                               'Restricted': len(restricted_accounts)
                           },
                           proxies_counter={
                               'Active': len(ProxyModel.getMany(current_session.id, [ProxyTypes.checker],
                                                                {'active': True})),
                               'In Active': len(ProxyModel.getMany(current_session.id, [ProxyTypes.checker],
                                                                   {'active': True}))
                           },
                           title="Checker")


def store():
    accounts_store_form = AccountStoreForm()
    message = {'type': 'danger', 'text': "Accounts hasn't uploaded."}
    if accounts_store_form.validate_on_submit():
        current_session = g.get('session')
        accounts = accounts_store_form.accounts_file.data.read().decode().split(
            "\n") if accounts_store_form.accounts_file.data else []

        if accounts_store_form.proxies_file.data:
            proxies = accounts_store_form.proxies_file.data.read().decode().split('\n')
            for proxy in proxies:
                proxy = proxy.strip()
                if proxy:
                    ip, port, username, password = proxy.split(':')
                    DatabaseThread.updateOrCreate(ProxyModel,
                                                  selector={
                                                      'session_id': current_session.id,
                                                      'proxy_ip': ip,
                                                      'proxy_port': port
                                                  },
                                                  data=dict(
                                                      session_id=current_session.id,
                                                      proxy_ip=ip,
                                                      proxy_port=port,
                                                      proxy_user=username,
                                                      proxy_password=password,
                                                      proxy_for='checker'
                                                  ))

        accounts_list = []

        for line in accounts:
            if line.strip():
                accounts_list.append(line.strip().split(":"))

        with current_app.app_context():
            CheckerWorker(current_user.id, current_session.id, accounts_list)

        message = {'type': 'success', 'text': 'Accounts has been uploaded'}

    db.session.close()
    flash(message)
    return redirect(url_for('checker.index'))


def accountsGenerator(**kwargs):
    current_session = g.get('session')
    text_file = ""
    filename = kwargs.pop('filename')
    accounts = current_session.accounts.filter_by(account_type=AccountTypes.checker, **kwargs).all()

    for account in accounts:
        text_file += f"{account.username}:{account.password}:{account.email}"
        text_file += f":{account.proxy_user}:{account.proxy_ip}:{account.proxy_port}\r\n" if all([account.proxy_user,
                                                                                                  account.proxy_ip,
                                                                                                  account.proxy_port]) \
            else "\r\n"
    AccountModel.deleteMany(current_session.id, [AccountTypes.checker], kwargs)
    return Response(text_file, mimetype="text/plain", headers={
        'Content-Disposition': f'attachment;filename={filename}.txt'
    })


def download():
    current_session = g.get('session')
    return accountsGenerator(session_id=current_session.id, **request.args)
