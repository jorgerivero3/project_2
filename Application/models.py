from Application import db, login_manager, application
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader # loads in user
def load_user(user_id):
	return User.query.get(int(user_id))

# Association Tables
friends = db.Table('friends', db.Column('self_id', db.Integer, db.ForeignKey('user.id')), db.Column('friend_id', db.Integer, db.ForeignKey('user.id')))
game_table = db.Table('games', db.Column("user_id", db.Integer, db.ForeignKey('user.id')), db.Column("game_id", db.Integer, db.ForeignKey('game.id'))) 

# Models 
class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	player1 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	score1 = db.Column(db.Integer, unique=False, nullable=False, default=0)
	player2 = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # need to take a look at this
	score2 = db.Column(db.Integer, unique=False, nullable=False, default=0)
	done = db.Column(db.Boolean, unique=False, nullable=False, default=False)
	over = db.Column(db.Boolean, unique=False, nullable=False, default=False)

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	games_won = db.Column(db.Integer(), nullable=False, default=0)
	friend_list = db.relationship("User", secondary=friends, primaryjoin = (friends.c.self_id == id), secondaryjoin = (friends.c.friend_id == id), backref= db.backref('friends', lazy='dynamic'), lazy='dynamic')
	games = db.relationship("Game", secondary=game_table, backref=db.backref('games', lazy='dynamic'))

	def add_friend(self, user): # allows user to add a friend and updates db
		if not self.is_friends(user) and self.id != user.id:
			self.friend_list.append(user)
			user.friend_list.append(self)

	def is_friends(self, user): # checks if users are already friends
		return self.friend_list.filter(friends.c.friend_id == user.id).count() > 0 

	def get_reset_token(self, expires_sec=1800): # for resetting password
		s = Serializer(application.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token): # verifies correct token for reset password
		s = Serializer(application.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}'')"
