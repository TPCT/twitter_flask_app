from Forms.dashboard.accounts.StoreForm import StoreForm as AccountStoreForm
from Forms.dashboard.proxies.StoreForm import StoreForm as ProxyStoreForm
from Workers.AccountValidationWorker import AccountValidationWorker
from Models.AccountModel import AccountModel
from Models.ProxyModel import ProxyModel
from Constants.AccountTypes import AccountTypes
from Constants.ProxyTypes import ProxyTypes
from flask import redirect, url_for, request, flash, current_app, Response, render_template, g
from flask_login import current_user


def index():
    accounts_store_form = AccountStoreForm()
    proxies_store_form = ProxyStoreForm()
    current_session = g.get('session')

    active_accounts = AccountModel.getAll(current_session.id,
                                           {'active': True, 'hidden': False})

    suspended_accounts = AccountModel.getAll(current_session.id,
                                              {'suspended': True})

    hidden_accounts = AccountModel.getAll(current_session.id,
                                           {'active': True, 'hidden': True})

    return render_template('Dashboard/Accounts.html',
                           title="Accounts",
                           accounts_form=accounts_store_form,
                           proxies_form=proxies_store_form,
                           accounts_counters={
                               'Active': len(active_accounts),
                               'Suspended': len(suspended_accounts),
                               'Hidden': len(hidden_accounts)
                           },
                           permissions=AccountTypes.getAllPermissionsNames([AccountTypes.checker]),
                           proxies_counter={
                               'Active': len(ProxyModel.getMany(current_session.id, [ProxyTypes.account], {
                                   'active': True
                               })),
                               'In-Active': len(ProxyModel.getMany(current_session.id, [ProxyTypes.account], {
                                   'active': False
                               }))
                           },
                           active_accounts=enumerate(active_accounts),
                           suspended_accounts=enumerate(suspended_accounts),
                           hidden_accounts=enumerate(hidden_accounts))


def store():
    accounts_store_form = AccountStoreForm()
    accounts_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Accounts hasn't uploaded."}
    available_permissions = AccountTypes.getAllPermissionsNames([AccountTypes.checker])
    request_permissions = [request.form.get(available_permissions[i]) for i in range(len(available_permissions))]
    account_type = 0

    if accounts_store_form.validate_on_submit() and any(request_permissions):
        accounts_list = []
        current_session = g.get('session')
        accounts = accounts_store_form.accounts_file.data.read().decode().split("\n")

        for i in range(len(available_permissions)):
            account_type += AccountTypes.getAccountType(available_permissions[i]) \
                if request.form.get(available_permissions[i]) else 0

        for account in accounts:
            if not account.strip():
                continue
            accounts_list.append((account_type, *account.strip().split(":")))

        with current_app.app_context():
            AccountValidationWorker(current_user.id, current_session.id, accounts_list)

        message = {'type': 'success', 'text': 'Accounts has been uploaded'}

    flash(message)
    return redirect(url_for('accounts.index'))


def delete(account_id):
    AccountModel.deleteOne(account_id)
    message = {'type': 'success', 'text': 'Account has been deleted'}
    flash(message)
    return redirect(url_for('accounts.index'))


def bulkDelete():
    AccountModel.deleteMany(g.get('session').id,
                            AccountTypes.getAll([AccountTypes.checker]),
                            request.args)
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('accounts.index'))


def accountsGenerator(**kwargs):
    filename = kwargs.pop('filename')
    accounts = AccountModel.getMany(g.get('session').id,
                                           AccountTypes.getAll([AccountTypes.checker]),
                                           kwargs)
    text_file = ""
    for account in accounts:
        text_file += f"{account.username}:{account.password}:{account.email}"
        text_file += (f":{account.proxy_ip}:{account.proxy_port}:"
                      f"{account.proxy_user}:{account.proxy_password}"
                      f"\r\n") if account.proxy_user else "\r\n"

    return Response(text_file, mimetype="text/plain", headers={
        'Content-Disposition': f'attachment;filename={filename}.txt'
    })


def download():
    current_session = g.get('session')
    return accountsGenerator(session_id=current_session.id, **request.args)
