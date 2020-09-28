from flask_wtf import FlaskForm
from wtforms import SubmitField, FloatField
from wtforms.validators import DataRequired


class OpPlanningForm(FlaskForm):
    coronal_component_C = FloatField('Enter coronal component C', validators=[DataRequired()])
    sagittal_component_S = FloatField('Enter sagittal component S', validators=[DataRequired()])
    torsion_component_T = FloatField('Enter torsion component T', validators=[DataRequired()])
    # filename = FileField('Store the results in:', validators=[Optional()])
    submit = SubmitField('Submit')
