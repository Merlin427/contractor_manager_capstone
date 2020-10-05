from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, Optional

class JobForm(FlaskForm):
    client_id = StringField(
        'client_id'
    )

    contractor_id = StringField(
        'contractor_id'
    )

    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )




class ContractorForm(FlaskForm):
    name = StringField(
        'name' validators=[DataRequired()]
    )

    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )




class ClientForm(FlaskForm):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )

    address = StringField(
        'name',
        validators=[DataRequired()]
    )

    phone = StringField(
        'phone',
        validators=[DataRequired()]
    )
