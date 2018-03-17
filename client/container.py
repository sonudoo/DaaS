import requests
import json
import click

def createContainer(authToken, url):
	serverAddress = url+"createContainer"
	data = dict()
	header = dict()
	while True:
		click.secho("Choose the container name: ")
		while True:
			data['containerName'] = input()
			if(data['containerName']!=''):
				break
			else:
				print('Container name cannot be empty! Try again..')

		header['Authorization'] = authToken
		print("Choose a container type:\n1. Blank Container\n2. Python Container: ")

		while True:
			data['containerType'] = input()
			if(data['containerType']=="1" or data['containerType']=="2"):
				break
			else:
				print('Invalid container type! Try again..')

		try:
			print("Please wait while your instance is being set up. This may take a minute or two.")
			check = requests.post(serverAddress, json=data, headers=header)
		except:
			print("Something went wrong. Please try again later..")
			return

		result = json.loads(check.text)

		if(result['success']==False):	
			print("Something went wrong. Please try again later..")
		else:
			print('Your container has been successfully created. Please use SSH to login to the server.')
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




