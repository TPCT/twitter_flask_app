from wtforms import SubmitField, StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    is_admin = BooleanField('is_admin', default=False)
    save = SubmitField('Save')