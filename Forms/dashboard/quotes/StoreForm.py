from wtforms import SubmitField, BooleanField, TextAreaField
from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm


class StoreForm(FlaskForm):
    quotes_text = FileField('quotes_file', validators=[FileAllowed(('txt', ))])
    fixed_quote_text = TextAreaField('quote_text', default='')
    random_quotes = BooleanField('random-quote', default=False)
    save = SubmitField('Save')