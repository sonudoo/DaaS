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
		
		print("Choose a Container Image:\n1. Blank Ubuntu Container\n2. Ubuntu Container with Python installed\n3. Ubuntu Container with Node installed\n ")

		while True:
			data['containerImage'] = input()
			if(int(data['containerImage']) >= 1 and int(data['containerImage']) <= 3):
				break
			else:
				print('Invalid container image selected! Try again..')

		print("Choose a Container Type:\n1. Processor: 1 vCPU, Memory: 1 GB\n2.Processor: 2 vCPUs, Memory: 2 GB\n")

		while True:
			data['containerType'] = input()
			if(int(data['containerType']) >= 1 and int(data['containerType']) <= 2):
				break
			else:
				print('Invalid container type selected! Try again..')

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
	try:
		check = requests.get(serverAddress, headers=header)
	except:
		print("Connection Error: Make sure that the server is reachable..\n")
		return

	result = json.loads(check.text)

	print("Your Container(s) list:\n")

	print("ContainerID\tName\tStatus")
	
	idx = 1
	for i in result:
		print("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper())
		idx += 1
	print()

def stopContainer(authToken, url):

	serverAddress = url+"getUserContainers"
	header = dict()
	header['Authorization'] = authToken

	try:
		check = requests.get(serverAddress, headers=header)
	except:
		print("Connection Error: Make sure that the server is reachable..\n")
		return

	result = json.loads(check.text)

	print("ContainerID\tName\tStatus")

	idx = 1

	mp = {}

	for i in result:
		if(i['status'] == "running"):
			mp[idx] = i['id']
			print("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper())
			idx += 1

	idx -= 1
	if(idx == 0):
		print("No containers available to stop\n")
		return

	i = -1
	while True:
		print("Enter the ID of the Container to stop: ")
		i = input()
		if(int(i)<=0 or int(i)>idx):
			print("Try again..")
		else:
			break

	data = dict()
	data['containerId'] = mp[int(i)]
	serverAddress = url+"stopContainer"
	try:
		check = requests.post(serverAddress, headers=header, json=data)
		result = json.loads(check.text)
		if(result['success']):
			print("The selected container has been successfully stopped..\n")
		else:
			print("Something went wrong. Please try again later..\n")
	except:
		print("Connection Error: Make sure that the server is reachable..\n")
		return




def startContainer(authToken, url):

	serverAddress = url+"getUserContainers"
	header = dict()
	header['Authorization'] = authToken

	try:
		check = requests.get(serverAddress, headers=header)
	except:
		print("Connection Error: Make sure that the server is reachable..\n")
		return

	result = json.loads(check.text)

	print("Select the Container to stop:\n")
	print("ContainerID\tName\tStatus")

	idx = 1

	mp = {}

	for i in result:
		if(i['status'] == "exited"):
			mp[idx] = i['id']
			print("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper())
			idx += 1

	idx -= 1

	if(idx == 0):
		print("All containers are already started.. No containers available to start..\n")
		return

	i = -1
	while True:
		print("Enter the ID of the Container to start: ")
		i = input()
		if(int(i)<=0 or int(i)>idx):
			print("Try again..")
		else:
			break

	data = dict()
	data['containerId'] = mp[int(i)]
	serverAddress = url+"startContainer"
	try:
		check = requests.post(serverAddress, headers=header, json=data)
		result = json.loads(check.text)
		if(result['success']):
			print("The selected container has been successfully started..\n")
		else:
			print("Something went wrong. Please try again later..\n")
	except:
		print("Connection Error: Make sure that the server is reachable..\n")
		return




