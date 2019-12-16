from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, SelectField, DateField, TextAreaField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from incidentlogger.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',
        validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    admin = BooleanField('Admin')
    confirm_password = PasswordField('Confirm Password',
        validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username not available, Please pick a different one.')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('An account has already been maid with that email. Please pick a different one or Login.')


class LoginForm(FlaskForm):
    email = StringField('Email',
        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class IncidentForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    submit = SubmitField('Confirm')

class GameForm(FlaskForm):
    picture = FileField('Upload Game Picture', validators=[FileAllowed(['jpg', 'png'])])
    system = StringField('System', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    descript = TextAreaField('Description', validators=[DataRequired()])
    tags = StringField('Tags', validators=[DataRequired()])
    rank = StringField('Rank', validators=[DataRequired()])
    date_released = DateField('Date Released', validators=[Optional()])
    submit = SubmitField('Confirm')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    rank = StringField('Rank', validators=[DataRequired()])
    submit = SubmitField('Post')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')



class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
