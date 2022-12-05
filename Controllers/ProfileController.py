from flask import render_template, g, request, Response, redirect, url_for, flash
from flask_login import current_user
from Forms.dashboard.profile.StoreForm import StoreForm as ProfileStoreForm
from Constants.AccountTypes import AccountTypes
from Constants.ImageTypes import ImageTypes
from Constants.TextTypes import TextTypes
from Constants.FileTypes import FileTypes
from Models.AccountModel import AccountModel
from Models.SettingsModel import SettingsModel
from Models.ImageModel import ImageModel
from Models.TextModel import TextModel
from Models.StorageModel import StorageModel
from Database.DatabaseWorker import DatabaseThread
from Workers.ProfileWorker import ProfileWorker
from config import db, threads_pool
from FileManagement.FileManagement import FileManagement


def index():
    current_session = g.get('session')
    status = current_session.status.first()
    settings = current_session.settings.first()
    profile_form = ProfileStoreForm()
    active_accounts = AccountModel.getMany(current_session.id, [AccountTypes.profile, AccountTypes.private], {
        'active': True, 'hidden': False
    })

    suspended_accounts = AccountModel.getMany(current_session.id, [AccountTypes.profile, AccountTypes.private], {
        'suspended': True
    })

    return render_template('Dashboard/Profile.html',
                           settings=settings,
                           title='Profile',
                           active_accounts=enumerate(active_accounts),
                           suspended_accounts=enumerate(suspended_accounts),
                           accounts_counters={
                               'Active': len(active_accounts),
                               'Suspended': len(suspended_accounts)
                           },
                           status_counters={
                               'Session Storage': {
                                   'Names': len(TextModel.getMany(current_session.id, [TextTypes.username])),
                                   'Bios': len(TextModel.getMany(current_session.id, [TextTypes.bio])),
                                   'Countries': len(TextModel.getMany(current_session.id, [TextTypes.country])),
                                   'Profile Pics': len(ImageModel.getMany(current_session.id,
                                                                          [ImageTypes.profile_picture])),
                                   'Profile Covers': len(ImageModel.getMany(current_session.id,
                                                                            [ImageTypes.profile_cover])),
                               },
                               'User Storage': {
                                   'Names': len(StorageModel.getMany(current_user.id, FileTypes.text,
                                                                     [TextTypes.username])),
                                   'Bios': len(StorageModel.getMany(current_user.id, FileTypes.text,
                                                                 [TextTypes.bio])),
                                   'Countries': len(StorageModel.getMany(current_user.id, FileTypes.text,
                                                                      [TextTypes.country])),
                                   'Profile Pics': len(StorageModel.getMany(current_user.id, FileTypes.images,
                                                                          [ImageTypes.profile_picture])),
                                   'Profile Covers': len(StorageModel.getMany(current_user.id, FileTypes.images,
                                                                            [ImageTypes.profile_cover])),
                               },
                               'Profile': {
                                   'Success': status.valid_profiles,
                                   'Failed': status.invalid_profiles
                               },
                               'Private': {
                                   'Success': status.valid_privates,
                                   'Failed': status.invalid_privates
                               }
                           },
                           profile_form=profile_form)


def store(session_id):
    profile_store_form = ProfileStoreForm()
    profile_store_form.process(formdata=request.form, data=request.files)
    message = {'type': 'danger', 'text': "Settings hasn't stored."}

    if profile_store_form.validate_on_submit():
        current_session = g.get('session')
        current_settings = current_session.settings.first()
        profile_covers = request.files.getlist('profile_covers_files')
        profile_pictures = request.files.getlist('profile_pictures_files')
        bio_files = request.files.getlist('profile_bio_files')
        usernames_file = profile_store_form.usernames_file.data.read().decode().split(
            '\n') if profile_store_form.usernames_file.data else []
        countries_file = profile_store_form.countries_file.data.read().decode().split(
            '\n') if profile_store_form.countries_file else []

        FileManagement.saveImages(current_session.id, profile_covers, 'session', ['profile_covers'], model=ImageModel,
                                  data={
                                      'session_id': session_id,
                                      'image_type': ImageTypes.profile_cover,
                                  }, extension='.jpg')

        FileManagement.saveImages(current_session.id, profile_pictures, 'session', ['profile_pictures'],
                                  model=ImageModel,
                                  data={
                                      'session_id': session_id,
                                      'image_type': ImageTypes.profile_picture,
                                  }, extension='.jpg')

        FileManagement.saveTexts(current_session.id, bio_files, 'session', ['profile_bios'], model=TextModel,
                                 data={'session_id': session_id, 'text_type': TextTypes.bio})

        FileManagement.splitAndSave(current_session.id, usernames_file, 'session',
                                    ['profile_usernames'], model=TextModel,
                                    data={'session_id': session_id, 'text_type': TextTypes.username})

        FileManagement.splitAndSave(current_session.id, countries_file, 'session',
                                    ['profile_countries'], model=TextModel,
                                    data={'session_id': session_id, 'text_type': TextTypes.country})

        DatabaseThread.updateOrCreate(SettingsModel,
                                      selector={
                                          'id': current_settings.id if current_settings else None,
                                          'session_id': session_id
                                      },
                                      data=dict(session_id=session_id,
                                                random_cover_images=bool(profile_store_form.random_profile_covers.data),
                                                random_profile_images=bool(
                                                    profile_store_form.random_profile_pictures.data),
                                                random_usernames=bool(profile_store_form.random_usernames.data),
                                                random_countries=bool(profile_store_form.random_countries.data),
                                                random_bios=bool(profile_store_form.random_bios.data),
                                                fixed_username_string=profile_store_form.username_fixed.data,
                                                fixed_country_string=profile_store_form.country_fixed.data,
                                                fixed_bio_string=profile_store_form.profile_bio_fixed.data))
        message = {'type': 'success', 'text': 'Settings has been stored'}

    flash(message)
    return redirect(url_for('profile.index'))


def process():
    current_session = g.get('session')
    thread = ProfileWorker
    message = {'type': 'danger', 'text': 'this operation is already added to the project'}

    if not threads_pool.get(current_user.id, {}).get(current_session.id, {}).get(ProfileWorker.__class__.__name__):
        thread(current_user.id, current_session.id)
        status_handler = current_session.status.first()

        status_handler.valid_profiles = 0
        status_handler.invalid_profiles = 0

        status_handler.valid_privates = 0
        status_handler.invalid_privates = 0

        db.session.flush()
        db.session.commit()
        message = {'type': 'success', 'text': 'this operation has been added to the project'}
    flash(message)
    return redirect(url_for('profile.index'))


def deleteAccount(account_id):
    AccountModel.deleteOne(account_id)
    message = {'type': 'success', 'text': 'Account has been deleted'}
    flash(message)
    return redirect(url_for('profile.index'))


def deleteAccounts():
    current_session = g.get('session')
    AccountModel.deleteMany(current_session.id, [AccountTypes.profile, AccountTypes.private], {})
    message = {'type': 'success', 'text': 'Accounts has been deleted'}
    flash(message)
    return redirect(url_for('profile.index'))


def deleteCoverImages():
    current_session = g.get('session')
    ImageModel.deleteMany(current_session.id, [ImageTypes.profile_cover])
    return redirect(url_for('profile.index'))


def deleteProfileImages():
    current_session = g.get('session')
    ImageModel.deleteMany(current_session.id, [ImageTypes.profile_picture])
    return redirect(url_for('profile.index'))


def deleteBio():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.bio])
    return redirect(url_for('profile.index'))


def deleteProfileNames():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.username])
    return redirect(url_for('profile.index'))


def deleteProfileCountries():
    current_session = g.get('session')
    TextModel.deleteMany(current_session.id, [TextTypes.country])
    return redirect(url_for('profile.index'))


def accountsGenerator(**kwargs):
    filename = kwargs.pop('filename')
    accounts = AccountModel.getMany(kwargs.pop('session_id'), [AccountTypes.profile, AccountTypes.private], kwargs)
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
