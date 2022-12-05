from wtforms import SubmitField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    proxies_file = FileField('proxies-file', validators=[FileAllowed(('txt', ))])
    save = SubmitField('Save')