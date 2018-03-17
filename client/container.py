import requests
import json
import click

def createContainer(authToken, url):
	serverAddress = url+"createContainer"
	data = dict()
	header = dict()
	while True:
		click.secho("Choose the container name: ", fg='green')
		while True:
			data['containerName'] = input()
			if(data['containerName']!=''):
				break
			else:
				click.secho('Container name cannot be empty! Try again..', fg='red')

		header['Authorization'] = authToken
		print("Choose a container type:\n1. Blank Container\n2. Python Container: ")

		while True:
			data['containerType'] = input()
			if(data['containerType']=="1" or data['containerType']=="2"):
				break
			else:
				click.secho('Invalid container type! Try again..', fg='red')

		try:
			click.secho("Please wait while your instance is being set up. This may take a minute or two.", fg='green')
			check = requests.post(serverAddress, json=data, headers=header)
		except:
			click.secho("Something went wrong. Please try again later..", fg='red')
			return

		result = json.loads(check.text)

		if(result['success']==False):	
			click.secho("Something went wrong. Please try again later..", fg='red')
		else:
			click.secho('Your container has been successfully created. Please use SSH to login to the server.', fg='green')
			print(result['ssh'])
			print()
			return

def listContainers(authToken, url):
	serverAddress = url+"getUserContainers"
	header = dict()
	header['Authorization'] = authToken
	check = requests.get(serverAddress, headers=header)
	result = json.loads(check.text)
	for i in result:
		print(i['name'])




