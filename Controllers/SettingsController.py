from flask import redirect, url_for, request, flash, g
from Forms.dashboard.settings.StoreForm import StoreForm as SettingsStoreForm
from Database.DatabaseWorker import DatabaseThread
from Models.SettingsModel import SettingsModel


def store(session_id):
    settings_store_form = SettingsStoreForm()
    settings_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Settings hasn't stored."}

    if settings_store_form.validate_on_submit() and all([
        int(settings_store_form.max_likes_count.data) >= int(settings_store_form.min_likes_count.data),
        int(settings_store_form.max_quotes_count.data) >= int(settings_store_form.min_quotes_count.data),
        int(settings_store_form.max_replies_count.data) >= int(settings_store_form.min_replies_count.data),
        int(settings_store_form.max_retweets_count.data) >= int(settings_store_form.min_retweets_count.data),
    ]):
        current_settings = g.get('session').settings.first()
        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={
                                          'id': current_settings.id if current_settings else None,
                                          'session_id': session_id
                                      },
                                      data=dict(
                                          session_id=session_id,
                                          min_likes_count=settings_store_form.min_likes_count.data,
                                          min_replies_count=settings_store_form.min_replies_count.data,
                                          min_quotes_count=settings_store_form.min_quotes_count.data,
                                          min_retweets_count=settings_store_form.min_retweets_count.data,
                                          max_likes_count=settings_store_form.max_likes_count.data,
                                          max_replies_count=settings_store_form.max_replies_count.data,
                                          max_quotes_count=settings_store_form.max_quotes_count.data,
                                          max_retweets_count=settings_store_form.max_retweets_count.data,
                                          tweets_time_sleep=settings_store_form.tweets_time_sleep.data,
                                          account_tweets_limit=settings_store_form.account_tweets_limit.data
                                      ))
        message = {'type': 'success', 'text': 'Settings has been stored'}

    flash(message)
    return redirect(url_for('reactions.index'))
