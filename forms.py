from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL, Optional

class JobForm(FlaskForm):
    client_id = StringField(
        'Client ID'
    )

    contractor_id = StringField(
        'Contractor ID'
    )

    start_time = DateTimeField(
        'Appointment date and time',
        validators=[DataRequired()],
        default= datetime.today()
    )




class ContractorForm(FlaskForm):
    name = StringField(
        'First and Last name', validators=[DataRequired()]
    )

    phone = StringField(
        'Phone Number',
        validators=[DataRequired()]
    )




class ClientForm(FlaskForm):
    name = StringField(
        'Customer Name',
        validators=[DataRequired()]
    )

    address = StringField(
        'Physical Address',
        validators=[DataRequired()]
    )

    phone = StringField(
        'Phone Number',
        validators=[DataRequired()]
    )
