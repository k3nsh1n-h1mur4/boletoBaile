from wtforms import Form, StringField, FileField
from wtforms.validators import DataRequired


class BoletoForm(Form):
    app = StringField('Apellido Paterno: ', validators=[DataRequired()])
    apm = StringField('Apellido Materno: ', validators=[DataRequired()])
    nombre = StringField('Nombre: ', validators=[DataRequired()])
    matricula = StringField('Matricula: ', validators=[DataRequired()])
    email = StringField('Email: ', validators=[DataRequired()])
    ine = FileField('INE:')
    tarjeton = FileField('Tarjetón de Pago(Última Qna):')
    acta_hijo = FileField('Acta de Nacimiento(Alguno de sus hijos(as)):')