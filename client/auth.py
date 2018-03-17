
import requests
import click
import json
import getpass


def register(url):
	serverAddress = url+"register"
	click.secho('--Register--', fg='red')
	data = dict()
	while  True:
		click.secho("Choose your username: ")
		data['username'] = input()
		data['password'] = getpass.getpass("Enter password: ")
		password_check = getpass.getpass("Confirm password: ")
		if(data['password'] != password_check):
			click.secho("Passwords didn't match. Please try again..", fg='red')
		else:
			try:
				click.secho("Registering..", fg='green')
				check = requests.post(serverAddress, json = data)
			except Exception as e:
				click.secho("Connection Error: Make sure that the server is reachable..", fg='red')

			result = json.loads(check.text)
			if(result['success']==False):	
				click.secho("Username already exists. Please try again..", fg='red')
			else:
				del data['password']
				data['url'] = url
				config_file = open('config.json', 'w')
				config_file.write(json.dumps(data))
				click.secho("You have been successfully registered. Please login to the server now.", fg='green')
				break



def login(url, username=""):
	serverAddress = url+"login"
	print(serverAddress)
	data = dict()
	while True:
		if(username==""):
			click.secho('--Login Details--', fg='red', bg='yellow')
			data['username'] = input('Username: ')
			data['password'] = getpass.getpass("Password: ")
			try:
				click.secho("Authenticating..", fg='green')
				token_req = requests.post(serverAddress, json = data)
			except Exception as e:
				click.secho("Connection Error: Make sure that the server is reachable..", fg='red')

			result = json.loads(token_req.text)
			if(result['success']):
				data['url'] = url
				del data['password']
				config_file = open('config.json', 'w')
				config_file.write(json.dumps(data))
				return result
			else:
				click.secho('Username/Password incorrect. Please try again..', fg='red')
		else:
			click.secho('--Login Details--', fg='red', bg='yellow')
			data['username'] = username
			data['password'] = getpass.getpass("Enter Password: ")
			try:
				click.secho("Authenticating..", fg='green')
				token_req = requests.post(serverAddress, json = data)
			except Exception as e:
				click.secho("Connection Error: Make sure that the server is reachable..", fg='red')
			result = json.loads(token_req.text)
			if(result["success"]):
				return result
			else:
				click.secho("Try again", fg='red')


