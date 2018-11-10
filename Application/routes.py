from flask import render_template, url_for, flash, redirect, request, abort
from Application import application, db, bcrypt, mail
from Application.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateInfo, AddFriend
from Application.models import User, Game
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
		user = User(username=form.username.data, email=form.email.data, password=hashed_password, games_won = 0)
		db.session.add(user)
		db.session.commit()
		flash('Account creation succesful!', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@application.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(url_for('home'))
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
	msg.body = f''' To reset your password, click the following link, or copy and paste it into your web browser: {url_for('reset_token', token=token, _external=True)} If you did not make this request then please ignore this email.'''
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

@application.route("/player_menu")
@login_required
## Loads the player's page with the list of friends
def player_menu():
	return render_template("player_menu.html")

@application.route("/friends", methods=['GET', 'POST'])
@login_required
def friends():
	form = AddFriend()
	if form.validate_on_submit():
		friend = User.query.filter_by(username=form.username.data).first()
		current_user.add_friend(friend)
		db.session.commit()
		flash('Friend Added!', 'success')
	return render_template("friendList.html", title="Friend's List", form=form)

@application.route('/active')
@login_required
def active():
	return render_template('active.html', title="Active Games")

######################
##### Game code ######
######################

@application.route("/create/<user>")
@login_required
def create(user): #creates game between players
	friend = User.query.filter_by(id=user).first()
	game = Game(player1=current_user.id, player2=friend.id)
	db.session.add(game)
	db.session.commit()
	return redirect('/friends/' + str(game.id))

@application.route("/friends/<id>/<number>")
@login_required
def save(id, number):
	game = Game.query.get_or_404(id)
	if current_user.id != game.player1 and current_user.id != game.player2:
		abort(403)
	if current_user.id == game.player1:
		game.score1 = number
		game.done = True
	else:
		game.score2 = number
		game.over = True
	db.session.commit()
	return redirect("/score/" + str(id))

@application.route("/score/<id>")
@login_required
def score(id):
	game = Game.query.get_or_404(id)
	if current_user != game.player1 and current_user != game.player2:
		abort(403)
	return render_template('score.html', title="score", game=game)

@application.route("/select")
def select():
	return render_template('select.html')

@application.route("/game/<number>", defaults={'correct': -1})
@application.route("/game/<number>/<correct>",)
def game(number, correct):
	# Retrieves Questions from the API
	questions = get_questions(number) #array of dictionaries
	for question in questions:
		question['incorrect_answers'].append(question['correct_answer'])
		random.shuffle(question['incorrect_answers'])
	return render_template('game.html', title='Quiz', questions=questions, correct=correct)

@application.route("/game/<number>/<score1>/<score2>")
def gameover(number, score1, score2):
	return render_template('gameover.html', title="Gameover", score1=score1, score2=score2)

@application.route("/friends/<id>")
@login_required
def friendgame(id):
	game = Game.query.get_or_404(id)
	if current_user.id != game.player1 and current_user.id != game.player2:
		abort(403)
	questions = get_questions("10")
	for question in questions:
		question['incorrect_answers'].append(question['correct_answer'])
		random.shuffle(question['incorrect_answers'])
	return render_template('friendgame.html', title='Quiz', questions=questions, game=game)
