from flask import render_template, g, redirect, request, url_for, flash, Response
from flask_login import current_user
from Forms.dashboard.replies.StoreForm import StoreForm as RepliesStoreForm
from Forms.dashboard.quotes.StoreForm import StoreForm as QuotesStoreForm
from Forms.dashboard.settings.StoreForm import StoreForm as SettingsStoreForm
from Models.AccountModel import AccountModel
from Models.TextModel import TextModel
from Models.StorageModel import StorageModel
from Constants.AccountTypes import AccountTypes
from Constants.FileTypes import FileTypes
from config import db
from Constants.TextTypes import TextTypes


def index():
    current_session = g.get('session')

    settings = current_session.settings.first()
    settings_store_form = SettingsStoreForm()
    replies_store_form = RepliesStoreForm()
    quotes_store_form = QuotesStoreForm()

    session_quotes = TextModel.getMany(current_session.id, [TextTypes.quote])

    session_replies = TextModel.getMany(current_session.id, [TextTypes.reply])

    user_quotes = StorageModel.getMany(current_session.id, FileTypes.text, [TextTypes.quote],
                                       settings.tweet_arabic)

    user_replies = StorageModel.getMany(current_session.id, FileTypes.text, [TextTypes.reply],
                                        settings.tweet_arabic)

    active_accounts = AccountModel.getMany(current_session.id, [AccountTypes.reply, AccountTypes.quote,
                                                                AccountTypes.react, AccountTypes.retweet],
                                           {'active': True})
    suspended_accounts = AccountModel.getMany(current_session.id, [AccountTypes.reply, AccountTypes.quote,
                                                                   AccountTypes.react, AccountTypes.retweet],
                                              {'suspended': True})

    return render_template('Dashboard/Reactions.html',
                           settings=settings,
                           title='Reactions',
                           accounts_counters={
                               'Active': len(active_accounts),
                               'Suspended': len(suspended_accounts)
                           },
                           status_counters={
                               'Session Storage': {
                                   'Quotes': len(session_quotes),
                                   'Replies': len(session_replies)
                               },
                               'User Storage': {
                                   'Quotes': len(user_quotes),
                                   'Replies': len(user_replies)
                               }
                           },
                           replies_form=replies_store_form,
                           quotes_form=quotes_store_form,
                           settings_form=settings_store_form,
                           active_accounts=enumerate(active_accounts),
                           suspended_accounts=enumerate(suspended_accounts))


def deleteAccount(account_id):
    AccountModel.deleteOne(account_id)
    message = {'type': 'success', 'text': 'Account has been deleted'}
    flash(message)
    return redirect(url_for('reactions.index'))


def deleteAccounts():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.reply, AccountTypes.quote,
                                                 AccountTypes.react, AccountTypes.retweet], {})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('reactions.index'))


def accountsGenerator(**kwargs):
    filename = kwargs.pop('filename')
    accounts = AccountModel.getMany(kwargs.pop('session_id'), [AccountTypes.reply, AccountTypes.quote,
                                                               AccountTypes.react, AccountTypes.retweet], kwargs)
    text_file = ""

    for account in accounts:
        text_file += f"{account.username}:{account.password}:{account.email}"
        text_file += f":{account.proxy_ip}:{account.proxy_port}:{account.proxy_user}:{account.proxy_password}\r\n" \
            if account.proxy_user else \
            "\r\n"

    return Response(text_file, mimetype="text/plain", headers={
        'Content-Disposition': f'attachment;filename={filename}.txt'
    })


def download():
    current_session = g.get('session')
    return accountsGenerator(session_id=current_session.id, **request.args)
