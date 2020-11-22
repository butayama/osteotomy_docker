from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange

info_message = 'use point (.) as decimal separator. Input range: -89 .. 89 degrees'

class OpPlanningForm(FlaskForm):
    coronal_component_C = FloatField('Enter coronal component C',
                                validators=[NumberRange(min=-89, max=89, message=info_message)])
    sagittal_component_S = FloatField('Enter sagittal component S',
                                validators=[NumberRange(min=-89, max=89, message=info_message)])
    torsion_component_T = FloatField('Enter torsion component T',
                                validators=[NumberRange(min=-89, max=89, message=info_message)])
    # filename = FileField('Store the results in:', validators=[Optional()])
    submit = SubmitField('Submit')
