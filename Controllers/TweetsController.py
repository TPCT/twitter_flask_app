from flask import redirect, url_for, request, flash, render_template, g, Response
from Database.DatabaseWorker import DatabaseThread
from Workers.TweetingWorker import TweetingWorker
from Forms.dashboard.tweets.StoreForm import StoreForm as TweetsStoreForm
from flask_login import current_user
from config import threads_pool, db
from Models.SettingsModel import SettingsModel
from Models.AccountModel import AccountModel
from Models.ImageModel import ImageModel
from Models.TextModel import TextModel
from Models.StorageModel import StorageModel
from Constants.ImageTypes import ImageTypes
from Constants.TextTypes import TextTypes
from Constants.AccountTypes import AccountTypes
from Constants.FileTypes import FileTypes
from FileManagement.FileManagement import FileManagement


def index():
    current_session = g.get('session')

    tweets_store_form = TweetsStoreForm()
    status = current_session.status.first()
    settings = current_session.settings.first()

    session_texts = TextModel.getMany(current_session.id, [TextTypes.tweet])
    session_images = ImageModel.getMany(current_session.id, [ImageTypes.tweet])

    storage_texts = StorageModel.getMany(current_user.id, FileTypes.text, [TextTypes.tweet], settings.tweet_arabic)
    storage_images = StorageModel.getMany(current_user.id, FileTypes.images, [ImageTypes.tweet], settings.tweet_arabic)

    active_accounts = AccountModel.getMany(current_session.id, [AccountTypes.tweet], {'active': True, 'hidden': False})
    active_accounts_count = len(active_accounts)

    suspended_accounts = AccountModel.getMany(current_session.id, [AccountTypes.tweet], {'suspended': True})
    suspended_accounts_counts = len(suspended_accounts)

    hidden_accounts = AccountModel.getMany(current_session.id, [AccountTypes.tweet], {'active': True, 'hidden': True})
    search_hidden_count = len(hidden_accounts)

    return render_template('Dashboard/Tweets.html',
                           settings=settings,
                           title="Tweets",
                           tweets_form=tweets_store_form,
                           accounts_counters={
                               'Active': active_accounts_count,
                               'Suspended': suspended_accounts_counts,
                               'Hidden': search_hidden_count
                           },
                           status_counters={
                               'Session Storage': {
                                   'Images': len(session_images),
                                   'Texts': len(session_texts)
                               },
                               'User Storage': {
                                   'Images': len(storage_images),
                                   'Texts': len(storage_texts)
                               },
                               'Tweets': {
                                   'Success': status.valid_tweets,
                                   'Failed': status.invalid_tweets
                               }
                           },
                           hidden_accounts=enumerate(hidden_accounts),
                           suspended_accounts=enumerate(suspended_accounts),
                           active_accounts=enumerate(active_accounts))


def store():
    tweets_store_form = TweetsStoreForm()
    tweets_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Tweets hasn't uploaded."}

    if tweets_store_form.validate_on_submit():
        current_session = g.get('session')
        current_settings = current_session.settings.first()

        text_files = request.files.getlist('tweets_texts')
        FileManagement.saveTexts(current_session.id, text_files, 'session', ['tweets'],
                                 model=TextModel, data={'session_id': current_session.id,
                                                        'text_type': TextTypes.tweet})

        image_files = request.files.getlist('tweets_images')
        FileManagement.saveImages(current_session.id, image_files, 'session', ['tweets'],
                                  model=ImageModel, data={'session_id': current_session.id,
                                                          'image_type': ImageTypes.tweet},
                                  extension='.jpg')

        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={
                                          'session_id': current_session.id,
                                          'id': current_settings.id if current_settings else None},
                                      data=dict(
                                          session_id=current_session.id,
                                          random_tweets=tweets_store_form.random_tweets.data,
                                          random_images=tweets_store_form.random_images.data,
                                          fixed_tweet_string=tweets_store_form.fixed_tweet_text.data,
                                          tweet_alt_text=tweets_store_form.alt_text.data,
                                          tweet_arabic=tweets_store_form.is_arabic.data
                                      ))
        message = {'type': 'success', 'text': 'Tweets has been uploaded'}

    flash(message)
    return redirect(url_for('tweets.index'))


def process():
    current_session = g.get('session')
    thread = TweetingWorker
    message = {'type': 'danger', 'text': 'this operation is already added to the project'}
    if not threads_pool.get(current_user.id, {}).get(current_session.id, {}).get(TweetingWorker.__class__.__name__):
        thread(current_user.id, current_session.id)
        status_handler = current_session.status.first()
        status_handler.valid_tweets = 0
        status_handler.invalid_tweets = 0

        status_handler.valid_quotes = 0
        status_handler.invalid_quotes = 0

        status_handler.valid_retweets = 0
        status_handler.invalid_retweets = 0

        status_handler.valid_reacts = 0
        status_handler.invalid_reacts = 0

        status_handler.valid_replies = 0
        status_handler.invalid_replies = 0
        db.session.flush()
        db.session.commit()
        message = {'type': 'success', 'text': 'this operation has been added to the project'}
    flash(message)
    return redirect(url_for('tweets.index'))


def deleteTweets():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.tweet])
    ImageModel.deleteMany(current_session.id, [ImageTypes.tweet])
    message = {'type': 'success', 'text': 'Tweets has been deleted'}
    flash(message)
    return redirect(url_for('tweets.index'))


def deleteAccount(account_id):
    AccountModel.deleteOne(account_id)
    message = {'type': 'success', 'text': 'Account has been deleted'}
    flash(message)
    return redirect(url_for('tweets.index'))


def deleteAccounts():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.tweet], {})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('tweets.index'))


def accountsGenerator(**kwargs):
    filename = kwargs.pop('filename')
    accounts = AccountModel.getMany(kwargs.pop('session_id'), [AccountTypes.tweet], kwargs)
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
