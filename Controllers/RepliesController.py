from flask import redirect, url_for, request, flash, g, current_app
from Forms.dashboard.replies.StoreForm import StoreForm as RepliesStoreForm
from Database.DatabaseWorker import DatabaseThread
from Models.SettingsModel import SettingsModel
from Models.TextModel import TextModel
from Constants.TextTypes import TextTypes
from FileManagement.FileManagement import FileManagement


def store():
    replies_store_form = RepliesStoreForm()
    replies_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Replies hasn't uploaded."}

    if replies_store_form.validate_on_submit():
        current_session = g.get('session')
        current_settings = current_session.settings.first()

        stream = replies_store_form.replies_text.data.read().decode().split(
            "\n") if replies_store_form.replies_text.data else []

        FileManagement.splitAndSave(current_session.id, stream, 'session', ['replies'], data={
            'session_id': current_session.id,
            'text_type': TextTypes.reply
        })

        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={'id': current_settings.id if current_settings else None,
                                                'session_id': current_session.id},
                                      model=TextModel,
                                      data=dict(
                                          session_id=current_session.id,
                                          random_replies=replies_store_form.random_replies.data,
                                          fixed_reply_string=replies_store_form.fixed_reply_text.data
                                      ))

        message = {'type': 'success', 'text': 'Replies has been uploaded'}

    flash(message)
    return redirect(url_for('reactions.index'))


def delete():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.reply])
    message = {'type': 'success', 'text': 'Replies has been deleted'}
    flash(message)
    return redirect(url_for('reactions.index'))
