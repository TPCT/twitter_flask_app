from flask import redirect, url_for, request, flash, render_template
from Forms.dashboard.dashboardSettings.StoreForm import StoreForm as SettingsStoreForm
from Models.StorageModel import StorageModel
from Constants.TextTypes import TextTypes
from Constants.ImageTypes import ImageTypes
from Constants.FileTypes import FileTypes
from flask_login import current_user
from FileManagement.FileManagement import FileManagement


def index():
    dashboard_settings_store_form = SettingsStoreForm()
    return render_template('Dashboard/Settings.html',
                           dashboard_settings_store_form=dashboard_settings_store_form,
                           title='Settings')


def store():
    settings_store_form = SettingsStoreForm()
    settings_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Settings hasn't stored."}

    if settings_store_form.validate_on_submit():
        # text_files = request.files.getlist('text_files')
        image_files = request.files.getlist('images_file')

        if (settings_store_form.text_files.data and not any([settings_store_form.text_for_quotes.data,
                                                             settings_store_form.text_for_replies.data,
                                                             settings_store_form.text_for_tweets.data,
                                                             settings_store_form.text_for_bios.data,
                                                             settings_store_form.text_for_usernames,
                                                             settings_store_form.text_for_countries])) or (
                image_files and not any([settings_store_form.images_for_tweets,
                                         settings_store_form.images_for_profile_covers,
                                         settings_store_form.images_for_profile_pictures])):
            flash(message)
            return redirect(url_for('dashboard_settings.index'))

        text_types = []
        text_type = 0
        if settings_store_form.text_for_tweets.data:
            text_types.append('tweets')
            text_type |= TextTypes.tweet
        if settings_store_form.text_for_quotes.data:
            text_types.append('quotes')
            text_type |= TextTypes.quote
        if settings_store_form.text_for_replies.data:
            text_types.append('replies')
            text_type |= TextTypes.reply
        if settings_store_form.text_for_bios.data:
            text_types.append('profile_bios')
            text_type |= TextTypes.bio
        if settings_store_form.text_for_usernames.data:
            text_types.append('profile_usernames')
            text_type |= TextTypes.username
        if settings_store_form.text_for_countries.data:
            text_types.append('profile_countries')
            text_type |= TextTypes.country

        stream = settings_store_form.text_files.data.read().decode().split(
            "\n") if settings_store_form.text_files.data else []

        FileManagement.splitAndSave(current_user.id, stream,
                                    'users', text_types, model=StorageModel, data={
                'user_id': current_user.id,
                'text_arabic': settings_store_form.text_arabic.data,
                'file_for': text_type,
                'file_type': FileTypes.text})

        image_type = 0
        image_types = []
        if settings_store_form.images_for_tweets.data:
            image_type |= ImageTypes.tweet
            image_types.append('tweets')
        if settings_store_form.images_for_profile_pictures.data:
            image_type |= ImageTypes.profile_picture
            image_types.append('profile_pictures')
        if settings_store_form.images_for_profile_covers.data:
            image_type |= ImageTypes.profile_cover
            image_types.append('profile_covers')

        FileManagement.saveImages(current_user.id, image_files,
                                  'users', image_types, model=StorageModel, data={
                'user_id': current_user.id,
                'text_arabic': settings_store_form.text_arabic.data,
                'file_for': image_type,
                'file_type': FileTypes.images})

        message = {'type': 'success', 'text': 'Settings has been stored'}

    flash(message)
    return redirect(url_for('dashboard_settings.index'))
