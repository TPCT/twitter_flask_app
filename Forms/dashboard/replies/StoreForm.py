from wtforms import SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    replies_text = FileField('replies_file', validators=[FileAllowed(('txt', ))])
    fixed_reply_text = TextAreaField('reply_text', default='')
    random_replies = BooleanField('random-reply', default=False)
    save = SubmitField('Save')