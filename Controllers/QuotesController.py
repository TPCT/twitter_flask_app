from flask import redirect, url_for, request, flash, g
from Forms.dashboard.quotes.StoreForm import StoreForm as QuotesStoreForm
from Database.DatabaseWorker import DatabaseThread
from Models.SettingsModel import SettingsModel
from Models.TextModel import TextModel
from Constants.TextTypes import TextTypes
from FileManagement.FileManagement import FileManagement


def store():
    quotes_store_form = QuotesStoreForm()
    quotes_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Quotes hasn't uploaded."}

    if quotes_store_form.validate_on_submit():
        current_session = g.get('session')
        current_settings = current_session.settings.first()

        stream = quotes_store_form.quotes_text.data.read().decode().split(
            "\n") if quotes_store_form.quotes_text.data else []

        FileManagement.splitAndSave(current_session.id, stream, 'session', ['quotes'], data={
                'session_id': current_session.id,
                'text_type': TextTypes.quote
            })

        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={
                                          'id': current_settings.id if current_settings else None,
                                          'session_id': current_session.id
                                      },
                                      model=TextModel,
                                      data=dict(
                                          session_id=current_session.id,
                                          random_quotes=quotes_store_form.random_quotes.data,
                                          fixed_quote_string=quotes_store_form.fixed_quote_text.data
                                      ))

        message = {'type': 'success', 'text': 'Quotes has been uploaded'}

    flash(message)
    return redirect(url_for('reactions.index'))


def delete():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.quote])
    message = {'type': 'success', 'text': 'Quotes has been deleted'}
    flash(message)
    return redirect(url_for('reactions.index'))
