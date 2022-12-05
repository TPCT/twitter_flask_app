from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    accounts_file = FileField('accounts', validators=[FileRequired(), FileAllowed(('txt', ))])
    save = SubmitField('Save')