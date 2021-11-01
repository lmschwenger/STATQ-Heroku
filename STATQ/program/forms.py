from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from STATQ.models import User



class UploadFileForm(FlaskForm):
    file = FileField(label='Tryk her eller træk fil til feltet', validators=[DataRequired(), FileAllowed(['csv', 'txt'])])
    submit = SubmitField('Upload')
    plotsubmit = SubmitField('Se Plot')
    plotstr = StringField()
    per_year = BooleanField('Vis Min, med og maks for hvert år')
    Qm_yr = FloatField(); Qm_s = FloatField(); Qm_v = FloatField(); 
    Qmin_yr = FloatField(); Qmin_s = FloatField(); Qmin_v = FloatField();
    Qmax_yr = FloatField(); Qmax_s = FloatField(); Qmax_v = FloatField(); 
#class ProcesFileForm(FlaskForm):

class ProcesFileForm(FlaskForm):
    Qm_yr = FloatField(); Qm_s = FloatField(); Qm_v = FloatField(); 
    Qmin_yr = FloatField(); Qmin_s = FloatField(); Qmin_v = FloatField();
    Qmax_yr = FloatField(); Qmax_s = FloatField(); Qmax_v = FloatField(); 
    rawplotstr = StringField()
    seasonplotstr = StringField()
    enkeltaarsplotstr = StringField()
    oneyearplotstr = StringField()
    Lokalitet=StringField()
    