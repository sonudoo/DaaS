import requests
import json
import click

def createNewDatabase(authToken, url):
	serverAddress = url+"createDatabase"
	data = dict()
	header = dict()
	while True:
		while True:
			click.secho("Enter database name: ")
			data['databaseName'] = input()
			if(data['databaseName']!=''):
				break
			else:
				click.secho('Database name cannot be empty! Try again..', fg='red')

		
		header['Authorization'] = authToken
		
		try:
			check = requests.post(serverAddress, json=data, headers=header)
		except:
			print("Connection error: Please make sure that the server is reachable.\n")



		result = json.loads(check.text)

		if(result['success']==False):	
			click.secho("The database name has already been taken. Please try again.", fg='red')
		else:
			click.secho("\nYour database has been successfully created.\n")
			print()
			return


