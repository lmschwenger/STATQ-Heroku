from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from STATQ.models import "User"


class RegistrationForm(FlaskForm):
    username = StringField('Brugernavn',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Kodeord', validators=[DataRequired()])
    confirm_password = PasswordField('Bekræft kodeord',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Opret bruger')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Brugernavnet er allerede i brug. Vælg venligst et andet.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Denne email er allerede i brug. Benyt venligst en anden.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Kodeord', validators=[DataRequired()])
    remember = BooleanField('Husk mig')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Brugernavn',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Opdatér')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Brugernavnet er allerede i brug. Vælg venligst et andet.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Denne email er allerede i brug. Vælg venligst en anden.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Nulstil kodeord her')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Der findes ingen bruger med denne email.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Kodeord', validators=[DataRequired()])
    confirm_password = PasswordField('Bekræft kodeord',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Nulstil kodeord')