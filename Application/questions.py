import requests
'''
#################

Trivia Questions API should be implemented here

#############
'''

#format https://opentdb.com/api.php?amount=10&category=10
#amounts (not limited by api) 5, 10, 15, 20
#categories books = 10, films = 11, science&nature = 17, sports = 21, animals = 27

def get_questions(number):
	link = "https://opentdb.com/api.php?amount=" + str(number)# + "&category=" + str(category)
	response = requests.get(link)
	return response.json()['results']
