from Application import db, login_manager, application
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

# Association Tables

friends = db.Table('friends', 
	db.Column('self_id', db.Integer, db.ForeignKey('user.id')), 
	db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
	)

game_table = db.Table('games', 
	db.Column("user_id", db.Integer, db.ForeignKey('user.id')),
	db.Column("game_id", db.Integer, db.ForeignKey('game.id'))
	) 

# Models 

class Game(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	current_turn = db.Column(db.Integer, db.ForeignKey('user.id'))
	next_turn = db.Column(db.Integer, db.ForeignKey('user.id'))
	current_score = db.Column(db.Integer, default=0)
	next_score = db.Column(db.Integer, default=0)


	def switch_turns(self):
		self.current_turn, self.next_turn = self.next_turn, self.current_turn
		self.current_score, self.next_score = self.next_score, self.current_score


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	games_won = db.Column(db.Integer(), nullable=False, default=0)
	friend_list = db.relationship(
		"User", secondary=friends,
		primaryjoin = (friends.c.self_id == id),
		secondaryjoin = (friends.c.friend_id == id), 
		backref= db.backref('friends', lazy='dynamic'), lazy='dynamic')
	games = db.relationship("Game", secondary=game_table, backref=db.backref('games', lazy='dynamic'))



	def add_friend(self, user):
		if not self.is_friends(user):
			self.friend_list.append(user)
			user.friend_list.append(self)

	def remove_friend(self, user):
		if self.is_friends(user):
			self.friend_list.remove(user)
			user.friend_list.remove(self)

	def is_friends(self, user):
		return self.friend_list.filter(friends.c.friend_id == user.id).count() > 0 

	def get_reset_token(self, expires_sec=1800):
		s = Serializer(application.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(application.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}'')"



