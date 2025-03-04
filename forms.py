from wtforms import Form, StringField
from wtforms.validators import DataRequired


class BoletoForm(Form):
    app = StringField('Apellido Paterno: ', validators=[DataRequired()])
    apm = StringField('Apellido Materno: ', validators=[DataRequired()])
    nombre = StringField('Nombre: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired()])