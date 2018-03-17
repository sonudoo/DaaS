import requests
import json
import click
from auth import login,register
from container import createContainer,listContainers, startContainer, stopContainer
from provider import registerAsProvider
import getpass
import inquirer
    

def operate(authToken, data):
	url = data['url']

	while True:
		questions = [
		  	inquirer.List('choice',
				message="Options",
				choices=['Create a new Container', 'Start a Container', 'Stop a Container', 'List my Containers', 'Register as a provider', 'EXIT'],
			),
		]
		answer = inquirer.prompt(questions)

		if(answer['choice']=="Create a new Container"):
			createContainer(authToken, url)

		elif(answer['choice'] == "List my Containers"):
			listContainers(authToken, url)

		elif(answer['choice'] == "Start a Container"):
			startContainer(authToken, url)

		elif(answer['choice'] == "Stop a Container"):
			stopContainer(authToken, url)

		elif(answer['choice'] == "Register as a provider"):
			registerAsProvider(authToken, url)

		else:
			break
     

@click.command()
def main():
	click.secho('--Docker as a Service--', fg='red', bg='white',blink = True)
	try:
		config_file = open('config.json', 'r')
	except:
		print("Configuration file doesn't exists.")

	try:
		data = json.load(config_file)
		url = data['url']
		if(("url" not in data) or data['url']==""):
			raise ValueError

		if(("username" in data) and data['username']!=""):
			login_result = login(url, data['username'])
		else:
			questions = [
			  	inquirer.List('size',
					message="Choose",
					choices=['LOGIN', 'REGISTER'],
				),
			]
			answer = inquirer.prompt(questions)
			if(answer['size']=='LOGIN'):
				login_result = login(url)
			else:
				register(url)
				login_result = login(url)

		authToken = login_result['token']
		operate(authToken, data)

	except Exception as e:
		print(e)    


if __name__=="__main__":
	main()