
'''
#################

Trivia Questions API should be implemented here

#############
'''

class Question:
	def __init__(self, question):
		self.category = CATEGORIES[question[0][0]]

		self.prompts = question[1][0]
		self.answers = question[1][1:]
		self.result = question[2]
		self.nextQuestion = question[3] #randomly select next question? #Need to remove self from question bank within a game
		self.image = question[4] #if we chose to have an image

	def get_next_Question(self, choice):
		#randomly select next question?
		return self.nextQuestion[choice]

	def num_choices(self):
		return len(self.prompts)



master = {}


CATEGORIES = {"g": "Geography", "e": "Entertainment", "s": "Sports", "h":"History", "a":"Arts", "r": "Random"}

#Scripts format: [0] == Category, [1] == Question + Answer choices, [2] == result of correct/wrong answer, [3] == next question
#s represents score
# example
g1 = ["g1", ["What is the capital city of New York?", "1. Harlem", "2. Albany", "3. New York City", "4. Rochester", "5. I plead the 5th"], [['-1s'], ['+1s'], ['-1s'], ['-1s'],['0s']], ['g2'], 'sleepy.gif']