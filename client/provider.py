import requests, json, click

def registerAsProvider(authToken, url):
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
		
		print("Choose a Container Image:\n1. Blank Ubuntu Container\n2. Ubuntu Container with Python installed:\n3. Ubuntu Container with Node installed:\n ")

		while True:
			data['containerImage'] = input()
			if(int(data['containerImage']) >= 1 and int(data['containerImage']) <= 3):
				break
			else:
				print('Invalid container image selected! Try again..')

		print("Choose a Container Type:\n1. 1 GB RAM")

		while True:
			data['containerType'] = input()
			if(int(data['containerType']) >= 1 and int(data['containerType']) <= 2):
				break
			else:
				print('Invalid container type selected! Try again..')

		try:
			print("Please wait while your instance is being set up. This may take a minute or two..")
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
