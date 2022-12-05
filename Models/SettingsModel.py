from config import db
from Models.BaseModel import BaseModel


class SettingsModel(db.Model, BaseModel):
    __tablename__ = "settings"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='CASCADE'), nullable=False)
    min_likes_count = db.Column(db.Integer, nullable=False, default=0)
    max_likes_count = db.Column(db.Integer, nullable=False, default=0)

    min_replies_count = db.Column(db.Integer, nullable=False, default=0)
    max_replies_count = db.Column(db.Integer, nullable=False, default=0)

    min_quotes_count = db.Column(db.Integer, nullable=False, default=0)
    max_quotes_count = db.Column(db.Integer, nullable=False, default=0)

    min_retweets_count = db.Column(db.Integer, nullable=False, default=0)
    max_retweets_count = db.Column(db.Integer, nullable=False, default=0)

    min_follow_count = db.Column(db.Integer, nullable=False, default=0)
    max_follow_count = db.Column(db.Integer, nullable=False, default=0)

    tweets_time_sleep = db.Column(db.Integer, nullable=False, default=5)
    account_tweets_limit = db.Column(db.Integer, nullable=False, default=1)

    random_replies = db.Column(db.BOOLEAN, default=True)
    random_tweets = db.Column(db.BOOLEAN, default=True)
    random_quotes = db.Column(db.BOOLEAN, default=True)
    random_images = db.Column(db.BOOLEAN, default=True)

    fixed_tweet_string = db.Column(db.VARCHAR(1024), default='')
    fixed_quote_string = db.Column(db.VARCHAR(1024), default='')
    fixed_reply_string = db.Column(db.VARCHAR(1024), default='')

    random_countries = db.Column(db.BOOLEAN, default=True)
    random_usernames = db.Column(db.BOOLEAN, default=True)
    random_bios = db.Column(db.BOOLEAN, default=True)
    random_cover_images = db.Column(db.BOOLEAN, default=True)
    random_profile_images = db.Column(db.BOOLEAN, default=True)

    fixed_username_string = db.Column(db.VARCHAR(255), default='')
    fixed_bio_string = db.Column(db.VARCHAR(255), default='')
    fixed_country_string = db.Column(db.VARCHAR(255), default='')

    notify = db.Column(db.BOOLEAN, default=False)

    tweet_alt_text = db.Column(db.VARCHAR(1024), default='')
    tweet_arabic = db.Column(db.BOOLEAN, default=False)
