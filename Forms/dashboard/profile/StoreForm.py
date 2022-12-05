from wtforms import SubmitField, BooleanField, TextAreaField, StringField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    usernames_file = FileField('usernames_file', validators=[FileAllowed(('txt', ))])
    countries_file = FileField('tweets_images', validators=[FileAllowed(('txt', ))])
    profile_pictures_files = FileField('profile_pictures')
    profile_covers_files = FileField('profile_covers')
    profile_bio_files = FileField('profile_bios_files')
    username_fixed = StringField('username_fixed', default='')
    country_fixed = StringField('country_fixed', default='')
    profile_bio_fixed = TextAreaField('profile_bio_fixed', default='')
    random_profile_pictures = BooleanField('random_pictures', default=False)
    random_profile_covers = BooleanField('random_covers', default=False)
    random_usernames = BooleanField('random_usernames', default=False)
    random_bios = BooleanField('random_bios', default=False)
    random_countries = BooleanField('random_countries', default=False)
    save = SubmitField('Save')