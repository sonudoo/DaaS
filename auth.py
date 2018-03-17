
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
			click.secho("Passwords didn't match. Please try again..")
		else:
			try:
				print("Registering..")
				check = requests.post(serverAddress, json = data)
			except Exception as e:
				print("Connection Error: Make sure that the server is reachable..")

			result = json.loads(check.text)
			if(result['success']==False):	
				print("Username already exists. Please try again..")
			else:
				del data['password']
				data['url'] = url
				config_file = open('config.json', 'w')
				config_file.write(json.dumps(data))
				print("You have been successfully registered. Please login to the server now.")
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
				print("Authenticating..")
				token_req = requests.post(serverAddress, json = data)
			except Exception as e:
				print("Connection Error: Make sure that the server is reachable..")

			result = json.loads(token_req.text)
			if(result['success']):
				data['url'] = url
				del data['password']
				config_file = open('config.json', 'w')
				config_file.write(json.dumps(data))
				return result
			else:
				print('Username/Password incorrect. Please try again..')
		else:
			click.secho('--Login Details--', fg='red', bg='yellow')
			data['username'] = username
			data['password'] = getpass.getpass("Enter Password: ")
			token_req = requests.post(serverAddress, json = data)
			result = json.loads(token_req.text)
			if(result["success"]):
				return result
			else:
				print("Try again")


