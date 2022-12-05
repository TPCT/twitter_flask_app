from wtforms import StringField, SubmitField
from wtforms.validators import InputRequired
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    name = StringField('name', validators=[InputRequired()])
    save = SubmitField('Save')