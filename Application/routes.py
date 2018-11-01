from flask import render_template, url_for, flash, redirect, request
from Application import application, db, bcrypt, mail
from Application.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateInfo
from Application.models import User
from flask_login import login_user, current_user, logout_user, login_required
import os
from flask_mail import Message
import sys
import random
from Application.questions import get_questions
@application.route('/')
def home():
	return render_template('/home.html', title='Trivia Game')

@application.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('game'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Account creation succesful!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@application.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('game'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(url_for('game'))
		else:
			flash('Login unsuccessful. Email and/or password incorrect.')
	return render_template('login.html', title='Login', form=form)

@application.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateInfo()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Info Updated', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	return render_template('account.html', title='Account Information', form=form)


@application.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


@application.route("/password_retrieval", methods=['GET', 'POST'])
def password_retrieval():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password', 'info')
		return redirect(url_for('login'))
	return render_template('password_retrieval.html', title='Reset Password', form=form)

def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com', recipients=[user.email])
	msg.body = f''' To reset your password, click the following link, or copy and
paste it into your web browser:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then please ignore this email.
'''
	mail.send(msg)

@application.route("/reset_token/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('The reset token you are using is invalid or expired.')
		return redirect(url_for('password_retrieval'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Password has been updated.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)

#Game code
@application.route("/game", methods=['GET', 'POST'])
#@login_required
def game():
	# Retrieves Questions from the API
	questions = get_questions() #array of dictionaries
	for question in questions:
		question['incorrect_answers'].append(question['correct_answer'])
		random.shuffle(question['incorrect_answers'])
	return render_template('game.html', title='Quiz', questions=questions)
	'''
	count = 0
	wrong = False
	# Game will continue to go until a wrong answer is given
	while not wrong:
		if count == len(questins):
			questions = get_questions() 
			count = 0
			continue
		question = questions[count]['question']
		answer = questions[count]['correct_answer']
		incorrect = questions[count]['incorrect_answers']
		incorrect.append(answer)
		choices = random.shuffle(incorrect)
		render_template('game.html', title="Trivia Game")
		count += 1
		'''
