
from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, length, Email, ValidationError, EqualTo
from Budgetio.Models import User


MONTHS = ['January','February', 'March', 'April', 'May', 'June', 'July', 'August', 'September','October','November', 'December']
TYPES = ['Income','Expenditure']


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max=20)], description='Username')
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username taken!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('email taken!')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Login')

class Trackerform(FlaskForm):
    month = SelectField(label='Select Month',choices=[(month) for month in MONTHS],validators=[DataRequired()])
    type = SelectField(label='Select Type', choices=[(type) for type in TYPES], validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired(), length(min=2, max=20)])
    expense = IntegerField('Enter Amount in Rupees',validators=[DataRequired()])
    submit = SubmitField('Enter')
    update = SubmitField('Update')

class Sorter(FlaskForm):
    month = SelectField(label='Select Month', choices=[(month) for month in MONTHS], validators=[DataRequired()])
    submit1 = SubmitField('Search')


class Updateuser(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), length(min=2, max=20)], description='Username')
    email = StringField('Email', validators=[DataRequired(), Email()])
    pic = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png'])])
    update = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username taken!')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('email taken!')
                
class Write_a_post(FlaskForm):
    headline = StringField('title', validators=[DataRequired(), length(min=2, max=30)], description='title')
    description = StringField('Description', validators=[DataRequired(), length(min=2, max=1000)])
    publish = SubmitField('Publish')
    edit = SubmitField('edit')

class delete_me(FlaskForm):
    delete_entries = BooleanField('Delete all my entries')
    delete_posts = BooleanField('Delete all my posts')
    delete_account = BooleanField('Delete my account (including all my data)')
    kill_me = SubmitField('I Confirm')