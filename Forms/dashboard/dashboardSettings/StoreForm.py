from wtforms import SubmitField, BooleanField
from flask_wtf.file import FileAllowed, FileField
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    text_files = FileField('text_files', validators=[FileAllowed(('txt', ))])
    text_arabic = BooleanField('text_arabic', default=False)
    text_for_tweets = BooleanField('text_for_tweets', default=False)
    text_for_quotes = BooleanField('text_for_quotes', default=False)
    text_for_replies = BooleanField('text_for_replies', default=False)
    text_for_bios = BooleanField('text_for_bios', default=False)
    text_for_usernames = BooleanField('text_for_usernames', default=False)
    text_for_countries = BooleanField('text_for_countries', default=False)
    images_file = FileField('images_file')
    images_for_tweets = BooleanField('images_for_tweets', default=False)
    images_for_profile_pictures = BooleanField('images_for_profile_pictures', default=False)
    images_for_profile_covers = BooleanField('images_for_profile_covers', default=False)
    save = SubmitField('Save')