from config import db
from Models.BaseModel import BaseModel


class StatusModel(db.Model, BaseModel):
    __tablename__ = "statuses"
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id', ondelete='cascade'), nullable=False)

    valid_tweets = db.Column(db.Integer, default=0)
    invalid_tweets = db.Column(db.Integer, default=0)

    valid_quotes = db.Column(db.Integer, default=0)
    invalid_quotes = db.Column(db.Integer, default=0)

    valid_retweets = db.Column(db.Integer, default=0)
    invalid_retweets = db.Column(db.Integer, default=0)

    valid_reacts = db.Column(db.Integer, default=0)
    invalid_reacts = db.Column(db.Integer, default=0)

    valid_replies = db.Column(db.Integer, default=0)
    invalid_replies = db.Column(db.Integer, default=0)

    valid_follows = db.Column(db.Integer, default=0)
    invalid_follows = db.Column(db.Integer, default=0)

    valid_profiles = db.Column(db.Integer, default=0)
    invalid_profiles = db.Column(db.Integer, default=0)

    valid_privates = db.Column(db.Integer, default=0)
    invalid_privates = db.Column(db.Integer, default=0)