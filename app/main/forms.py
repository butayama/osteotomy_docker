from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField
from wtforms.validators import NumberRange

info_message = 'use point (.) as decimal separator. Input range: -89 .. 89 degrees'


class CalculateForm(FlaskForm):
    coronal_component_C = FloatField('Coronal component C',
                                     validators=[NumberRange(min=-89, max=89, message=info_message)])
    sagittal_component_S = FloatField('Sagittal component S',
                                      validators=[NumberRange(min=-89, max=89, message=info_message)])
    torsion_component_T = FloatField('Torsion component T',
                                     validators=[NumberRange(min=-89, max=89, message=info_message)])
    # filename = FileField('Store the results in:', validators=[Optional()])
    submit = SubmitField('Submit')
