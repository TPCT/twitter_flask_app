from flask import redirect, url_for, request, flash, g
from Forms.dashboard.proxies.StoreForm import StoreForm as ProxiesStoreForm
from Database.DatabaseWorker import DatabaseThread
from Models.ProxyModel import ProxyModel
from Constants.ProxyTypes import ProxyTypes
from Constants.ProxyTypes import ProxyTypes


def store(proxy_for):
    proxies_store_form = ProxiesStoreForm()
    proxies_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Proxies hasn't uploaded."}

    if proxies_store_form.validate_on_submit():
        current_session = g.get('session')
        stream = proxies_store_form.proxies_file.data.read().decode().split(
            "\n") if proxies_store_form.proxies_file.data else []

        for i in range(0, len(stream)):
            text = stream[i].strip()
            if not text:
                continue

            proxy_ip, proxy_port, proxy_user, proxy_password = text.split(":")[:4]
            DatabaseThread.updateOrCreate(ProxyModel,
                                          selector={
                                              'session_id': current_session.id,
                                              'proxy_ip': proxy_ip,
                                              'proxy_port': proxy_port
                                          },
                                          data=dict(
                                              session_id=current_session.id,
                                              proxy_user=proxy_user,
                                              proxy_password=proxy_password,
                                              proxy_ip=proxy_ip,
                                              proxy_port=proxy_port,
                                              proxy_for=ProxyTypes.account if proxy_for == 'account' else ProxyTypes.checker
                                          ))

        message = {'type': 'success', 'text': 'Proxies has been uploaded'}

    flash(message)
    return redirect(url_for('accounts.index' if proxy_for == 'account' else 'checker.index'))


def delete(proxy_for):
    current_session = g.get('session')
    ProxyModel.deleteMany(current_session.id, [ProxyTypes.account], {})
    message = {'type': 'success', 'text': 'Proxies has been deleted'}
    flash(message)
    return redirect(url_for('accounts.index' if proxy_for == 'account' else 'checker.index'))
