import requests
'''
#################

Trivia Questions API should be implemented here

#############
'''


def get_questions():
	response = requests.get("https://opentdb.com/api.php?amount=10")
	return response.json()['response']
