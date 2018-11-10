from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, ValidationError
from Application.models import User
from flask_login import current_user


class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('Username Taken. Try again')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('Email Taken. Try again')


class LoginForm(FlaskForm): #do we want to change to login by username?
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')
		
class RequestResetForm(FlaskForm):
	email = StringField("Email", validators=[DataRequired(), Email()])
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError("No such account with that email exists.")

class ResetPasswordForm(FlaskForm):
	password = PasswordField("New Password", validators=[DataRequired()])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Reset Password')

class UpdateInfo(FlaskForm):
	username = StringField("Username: ", validators=[DataRequired()])
	email = StringField("Email: ", validators=[DataRequired(), Email()])
	submit = SubmitField('Update Info')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('Username Taken')

	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('Email taken')

class AddFriend(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	submit = SubmitField('Add Friend')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is None:
			raise ValidationError("User does not exist.")
		if current_user.id == user.id:
			raise ValidationError("Cannot add yourself!")
				