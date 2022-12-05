from wtforms import SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    tweets_texts = FileField('tweets_texts', validators=[FileAllowed(('txt', ))])
    tweets_images = FileField('tweets_images')
    fixed_tweet_text = TextAreaField('fixed_tweet_string', default='')
    alt_text = TextAreaField('alt_text', default='')
    random_images = BooleanField('random-image', default=False)
    random_tweets = BooleanField('random-tweets', default=False)
    is_arabic = BooleanField('is_arabic', default=False)
    save = SubmitField('Save')