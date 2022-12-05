from flask import render_template, g, request, Response, redirect, url_for, flash, current_app
from flask_login import current_user
from Forms.dashboard.follow.StoreForm import StoreForm as FollowStoreForm
from Constants.AccountTypes import AccountTypes
from Models.SettingsModel import SettingsModel
from Models.AccountModel import AccountModel
from Workers.FollowWorker import FollowWorker
from Database.DatabaseWorker import DatabaseThread
from API.AccountSearch import AccountSearch
from config import db, threads_pool
from concurrent.futures import ThreadPoolExecutor
from API.TwitterAccount import TwitterAccount
import random


def index():
    current_session = g.get('session')
    status = current_session.status.first()
    settings = current_session.settings.first()
    followers_form = FollowStoreForm()
    to_be_followed_accounts = AccountModel.getMany(current_session.id, [AccountTypes.followed], {'active': True})
    followers_accounts = AccountModel.getMany(current_session.id, [AccountTypes.follower], {'active': True})
    success_accounts = AccountModel.getMany(current_session.id, [AccountTypes.followed], {'active': True,
                                                                                          'follow_failed': -1})
    return render_template('Dashboard/Follow.html',
                           settings=settings,
                           title='Follows',
                           follow_counters={
                               'To Be Followed': len(to_be_followed_accounts),
                               'Followers': len(followers_accounts)
                           },
                           status_counters={
                               'Follow': {
                                   'Success': status.valid_follows,
                                   'Failed': status.invalid_follows
                               }
                           },
                           to_be_followed_accounts=enumerate(to_be_followed_accounts),
                           followers_accounts=enumerate(followers_accounts),
                           success_accounts=enumerate(success_accounts),
                           followers_form=followers_form)


def check():
    current_session = g.get('session')
    followers_accounts = AccountModel.getMany(current_session.id, [AccountTypes.follower], {'active': True})
    to_be_followed = AccountModel.getMany(current_session.id, [AccountTypes.followed], {'active': True})

    min_followers_count = current_session.settings.first().min_follow_count
    max_followers_count = current_session.settings.first().min_follow_count

    response_accounts = {
        'less': [],
        'high': [],
        'equal': []
    }

    for account in to_be_followed:
        for i in range(5):
            follower_account: AccountModel = random.choice(followers_accounts)
            twitter_wrapper: TwitterAccount = follower_account.twitter_wrapper()
            account_followers = twitter_wrapper.follow(account.account_id)
            if account_followers and account_followers:
                account_followers = account_followers.get('followers_count')
                if account_followers < min_followers_count:
                    response_accounts['less'].append(account.username)
                elif account_followers > max_followers_count:
                    response_accounts['high'].append(account.username)
                else:
                    response_accounts['equal'].append(account.username)
                break
    return response_accounts


def store(session_id):
    follow_store_form = FollowStoreForm()
    follow_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Settings hasn't stored."}
    current_settings = g.get('session').settings.first()

    if follow_store_form.validate_on_submit() and \
            int(follow_store_form.max_followers_count.data) >= int(follow_store_form.min_followers_count.data):

        if follow_store_form.accounts_file.data:
            account_search_handler = AccountSearch()

            def handler_thread(**kwargs):
                if not kwargs.get('username'):
                    return

                nonlocal account_search_handler
                account_id = account_search_handler.checkAccount(f"{kwargs['username']}")

                while not account_id:
                    account_search_handler = AccountSearch()
                    account_id = account_search_handler.checkAccount(f"{kwargs['username']}")

                del account_id['followers_count']

                DatabaseThread.updateOrCreate(AccountModel,
                                              selector=dict(session_id=session_id,
                                                            username=kwargs.get('username')),
                                              data=dict(session_id=session_id,
                                                        **account_id,
                                                        account_type=AccountTypes.followed,
                                                        **kwargs))

            stream = follow_store_form.accounts_file.data.read().decode('utf-8').split(
                '\n') if follow_store_form.accounts_file.data else []

            with ThreadPoolExecutor(50) as executor:
                threads_pool_ = []
                for line in stream:
                    if not line:
                        continue

                    data = {'username': None, 'password': None, 'email': None,
                            'proxy_ip': None, 'proxy_port': None,
                            'proxy_user': None, 'proxy_password': None}

                    account_keys = list(data.keys())

                    line = line.strip().split(':')

                    for i in range(len(line)):
                        data[account_keys[i]] = line[i]

                    with current_app.app_context():
                        threads_pool_.append(executor.submit(handler_thread, **data))

        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={
                                          'session_id': session_id,
                                          'id': current_settings.id if current_settings else None
                                      }, data=dict(session_id=session_id,
                                                   min_follow_count=follow_store_form.min_followers_count.data,
                                                   max_follow_count=follow_store_form.max_followers_count.data,
                                                   notify=follow_store_form.notify.data))
        message = {'type': 'success', 'text': 'Settings has been stored'}

    flash(message)
    return redirect(url_for('follow.index'))


def process():
    current_session = g.get('session')
    thread = FollowWorker
    message = {'type': 'danger', 'text': 'this operation is already added to the project'}

    if not threads_pool.get(current_user.id, {}).get(current_session.id, {}).get(FollowWorker.__class__.__name__):
        thread(current_user.id, current_session.id)
        status_handler = current_session.status.first()
        status_handler.valid_follows = 0
        status_handler.invalid_follows = 0
        db.session.flush()
        db.session.commit()
        message = {'type': 'success', 'text': 'this operation has been added to the project'}
    flash(message)
    return redirect(url_for('follow.index'))


def deleteAccount(account_id):
    AccountModel.deleteOne(account_id)
    message = {'type': 'success', 'text': 'Account has been deleted'}
    flash(message)
    return redirect(url_for('follow.index'))


def deleteToBeFollowed():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.followed], {})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('follow.index'))


def deleteFollowers():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.follower], {})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('follow.index'))


def deleteFailed():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.followed], {'follow_failed': -1})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('follow.index'))


def accountsGenerator(**kwargs):
    account_type = kwargs.pop('account_type')
    filename = kwargs.pop('filename')
    accounts = AccountModel.getMany(kwargs.pop('session_id'),
                                    [AccountTypes.followed if account_type == 'Followed' else AccountTypes.follower],
                                    kwargs)
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
