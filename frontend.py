import requests
import json
import click
from auth import login,register
from container import createContainer,listContainers
import getpass
import inquirer
    

def operate(authToken, data):
	url = data['url']

	while True:
		questions = [
		  	inquirer.List('choice',
				message="Options",
				choices=['Create Containers', 'List my containers', 'EXIT'],
			),
		]
		answer = inquirer.prompt(questions)
		if(answer['choice']=="Create Containers"):
			createContainer(authToken, url)
		elif(answer['choice'] == "List my containers"):
			listContainers(authToken, url)
		else:
			break
     

@click.command()
def main():
	click.secho('--Docker as a Service--', fg='red', bg='white',blink = True)
	try:
		config_file = open('config.json', 'r')
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
		print("Configuration file doesn't exists.")
	    


if __name__=="__main__":
	main()