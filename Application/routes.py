from Application import application, db, bcrypt, mail
from Application.forms import RegistrationForm, LoginForm, RequestResetForm, ResetPasswordForm, UpdateInfo, AddFriend
from Application.models import User, Game
from Application.questions import get_questions
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import os
import sys
import random


@application.route('/')
def home():
	return render_template('/home.html', title='Trivia Game')

@application.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('game'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8') # encrypt password
		user = User(username=form.username.data, email=form.email.data, password=hashed_password, games_won = 0) # create object
		db.session.add(user) # add to db
		db.session.commit() # update db
		flash('Account creation succesful!', 'success') # notify user
		return redirect(url_for('login')) # so you user can now log in
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
			next_page = request.args.get('next') # if redirected from another page, return them to that page
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
		form.username.data = current_user.username # fills in form with current username
		form.email.data = current_user.email # fills in form with current email
	return render_template('account.html', title='Account Information', form=form)

@application.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

@application.route("/friends", methods=['GET', 'POST']) #friends list that allows for adding friends
@login_required
def friends():
	form = AddFriend()
	if form.validate_on_submit():
		friend = User.query.filter_by(username=form.username.data).first() # find object for given username
		current_user.add_friend(friend) # add friend in db (from object)
		db.session.commit() # update db
		flash('Friend Added!', 'success')
	return render_template("friendList.html", title="Friend's List", form=form)

@application.route('/active') # shows current user their "active" games
@login_required
def active():
	return render_template('active.html', title="Active Games", User=User)

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


######################
##### Game code ######
######################


##### LOCAL GAMES #####

@application.route("/select") # select the number of questions (local only)
def select():
	return render_template('select.html')

@application.route("/game/<number>", defaults={'correct': -1})
@application.route("/game/<number>/<correct>",)
def game(number, correct):
	questions = get_questions(number) # retrieves questions from API
	for question in questions:
		question['incorrect_answers'].append(question['correct_answer'])
		random.shuffle(question['incorrect_answers']) # shuffles correct answer into choices
	return render_template('game.html', title='Quiz', questions=questions, correct=correct)

@application.route("/game/<number>/<score1>/<score2>") #displays local play scores
def gameover(number, score1, score2):
	return render_template('gameover.html', title="Gameover", score1=score1, score2=score2)


##### ONLINE GAMES #####

@application.route("/create/<user>")
@login_required
def create(user): # creates game between players
	friend = User.query.filter_by(id=user).first() # find friend object
	game = Game(player1=current_user.id, player2=friend.id) # create game object
	current_user.games.append(game) # update players in db to have this game
	friend.games.append(game)
	db.session.add(game) # add game to db
	db.session.commit() # update db
	return redirect('/friends/' + str(game.id)) # redirect after game is created so they can play

@application.route("/friends/<id>")
@login_required
def friendgame(id): # plays online game with a given ID
	game = Game.query.get_or_404(id) # makes sure game exists
	if current_user.id != game.player1 and current_user.id != game.player2: # makes sure player is on game
		abort(403)
	questions = get_questions("10") # set number of questions, no option to choose
	for question in questions:
		question['incorrect_answers'].append(question['correct_answer'])
		random.shuffle(question['incorrect_answers'])
	return render_template('friendgame.html', title='Quiz', questions=questions, game=game)

@application.route("/friends/<id>/<number>") 
@login_required
def save(id, number): # saves the score of a player to the game
	game = Game.query.get_or_404(id) # make sure game exists
	if current_user.id != game.player1 and current_user.id != game.player2: # make sure they're on the game
		abort(403)
	if current_user.id == game.player1: # update game score
		game.score1 = number
		game.done = True
	else: # update game score
		game.score2 = number
		game.over = True
		if int(game.score1) > int(game.score2):
			User.query.filter_by(id=game.player1).first().games_won += 1
		elif int(game.score1) < int(game.score2):
			User.query.filter_by(id=game.player2).first().games_won += 1
	db.session.commit()
	return redirect("/score/" + str(id)) # displays scores after done saving

@application.route("/score/<id>")
@login_required
def score(id): # page that displays scores. If haven't played, default=0
	game = Game.query.get_or_404(id)
	if current_user.id != game.player1 and current_user.id != game.player2:
		abort(403)
	return render_template('score.html', title="score", game=game, User=User)
