from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User

class ProductForm(FlaskForm):
    description = StringField(_l('Description'), validators=[DataRequired()])
    barcode = StringField(_l('Barcode'))
    update = SubmitField('Save')



class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')