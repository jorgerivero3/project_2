import requests


def get_questions(number): # pulls questions from online API
#format https://opentdb.com/api.php?amount=10&category=10
#amounts (not limited by api, defined in /select route) 5, 10, 15, 20
	link = "https://opentdb.com/api.php?amount=" + str(number)
	response = requests.get(link)
	return response.json()['results'] # returns question without response code
