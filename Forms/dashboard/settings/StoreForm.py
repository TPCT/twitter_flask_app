from wtforms import SubmitField, IntegerField, BooleanField, TextAreaField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    min_likes_count = IntegerField('min_likes_count', validators=[InputRequired()])
    min_replies_count = IntegerField('min_replies_count', validators=[InputRequired()])

    min_retweets_count = IntegerField('min_retweets_count', validators=[InputRequired()])
    min_quotes_count = IntegerField('min_quotes_count', validators=[InputRequired()])

    max_likes_count = IntegerField('max_likes_count', validators=[InputRequired()])
    max_replies_count = IntegerField('max_replies_count', validators=[InputRequired()])

    max_retweets_count = IntegerField('max_retweets_count', validators=[InputRequired()])
    max_quotes_count = IntegerField('max_quotes_count', validators=[InputRequired()])

    random_replies = BooleanField('random_replies')
    random_quotes = BooleanField('random_quotes')
    random_tweets = BooleanField('random_tweets')

    fixed_quote_text = TextAreaField('fixed_quote_string')
    fixed_tweet_text = TextAreaField('fixed_tweet_string')
    fixed_reply_text = TextAreaField('fixed_reply_string')

    tweets_time_sleep = IntegerField('sleep_between_retweets', validators=[InputRequired()])
    account_tweets_limit = IntegerField('account_tweets_limit', validators=[InputRequired()])
    save = SubmitField('Save')