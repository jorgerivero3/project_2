import unittest
from Application import application, db
from Application.models import User, friends

class UserModel(unittest.TestCase):

	def setUp(self):
		application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
		db.create_all()

	def tearDown(self):
		db.session.remove()
		db.drop_all()

	def test_add_friend(self):
		u1 = User(username="Player1", email="ayy@lmao.com", password="cat", games_won=0)
		u2 = User(username="Player2", email="me@me.com", password="dog", games_won=0)
		db.session.add(u1)
		db.session.add(u2)
		db.session.commit()
		self.assertEqual(u1.friend_list.all(), [])
		self.assertEqual(u2.friend_list.all(), [])

		u1.add_friend(u2)
		db.session.commit()
		self.assertTrue(u1.is_friends(u2))
		self.assertEqual(u1.friend_list.count(), 1)
		self.assertEqual(u1.friend_list.first().username, "Player2")
		self.assertEqual(u2.friend_list.count(), 1)
		self.assertEqual(u2.friend_list.first().username, "Player1")

		u1.remove_friend(u2)
		db.session.commit()
		self.assertFalse(u1.is_friends(u2)) 
