#!/usr/bin/python3
"""
    classes for the Forms used
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from appmodels.models import User

TYPE_CHOICES = [('Tutor', 'becoming a Tutor'), ('Parent', 'hiring a Tutor')]

class RegistrationForm(FlaskForm):
    """
    A class representation of Registration Form
    """
    first_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    user_type = SelectField(u'I\'m interested in: ', choices=TYPE_CHOICES)
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    """
    A class representation of Login Form
    """
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class UpdateParentProfileForm(FlaskForm):
    """
    A class representation of form to update profile of non-tutor
    """
    first_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

class UpdateProfileForm(FlaskForm):
    """
    A class representation of form to update profile of tutor
    """
    first_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    rate = FloatField('Rate/hour',
                        validators=[DataRequired()])
    bio =  TextAreaField(u'Qualification', validators=[DataRequired()])
    header = TextAreaField(u'Summary')
    lang = TextAreaField(u'Working Language')
    placesofresidence = TextAreaField(u'Place of Work')
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
                
class RequestResetForm(FlaskForm):
    """
    A class representation of password reset request form
    """
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    """
    A class representation of password reset form
    """
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm new Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
