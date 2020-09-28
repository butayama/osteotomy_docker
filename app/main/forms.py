from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField
from wtforms.validators import DataRequired, NumberRange


class OpPlanningForm(FlaskForm):
    coronal_component_C = FloatField('Enter coronal component C',
                                validators=[NumberRange(min=-89, max=89, message='input range: -89 .. 89 degrees')])
    sagittal_component_S = FloatField('Enter sagittal component S',
                                validators=[NumberRange(min=-89, max=89, message='input range: -89 .. 89 degrees')])
    torsion_component_T = FloatField('Enter torsion component T',
                                validators=[NumberRange(min=-89, max=89, message='input range: -89 .. 89 degrees')])
    # filename = FileField('Store the results in:', validators=[Optional()])
    submit = SubmitField('Submit')
