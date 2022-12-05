from wtforms import IntegerField, SubmitField, BooleanField
from flask_wtf.file import FileAllowed, FileField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    accounts_file = FileField('accounts_file', validators=[FileAllowed(('txt', ))])
    min_followers_count = IntegerField('min_followers_count', validators=[InputRequired()])
    max_followers_count = IntegerField('max_follower_count', validators=[InputRequired()])
    notify = BooleanField('notify')
    save = SubmitField('Save')