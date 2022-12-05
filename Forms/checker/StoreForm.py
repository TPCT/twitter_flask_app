from wtforms import SubmitField
from flask_wtf.file import FileField, FileRequired
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    accounts_file = FileField('accounts', validators=[FileRequired()])
    proxies_file = FileField('proxies')
    save = SubmitField('Save')