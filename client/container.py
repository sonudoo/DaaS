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
				click.secho('Container name cannot be empty! Try again..', fg='red')

		header['Authorization'] = authToken
		
		click.secho("Choose a Container Image:\n1. Blank Ubuntu Container\n2. Ubuntu Container with Python installed\n3. Ubuntu Container with Node installed\n ")

		while True:
			data['containerImage'] = input()
			if(int(data['containerImage']) >= 1 and int(data['containerImage']) <= 3):
				break
			else:
				click.secho('Invalid container image selected! Try again..', fg='red')

		click.secho("Choose a Container Type:\n1. Processor: 1 vCPU, Memory: 1 GB\n2.Processor: 2 vCPUs, Memory: 2 GB\n")

		while True:
			data['containerType'] = input()
			if(int(data['containerType']) >= 1 and int(data['containerType']) <= 2):
				break
			else:
				click.secho('Invalid container type selected! Try again..', fg='red')

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
			click.secho(result['ssh'])
			print()
			return

def listContainers(authToken, url):
        serverAddress = url+"getUserContainers"
        header = dict()
        header['Authorization'] = authToken
        try:
                check = requests.get(serverAddress, headers=header)
        except:
                click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
                return

        result = json.loads(check.text)

        click.secho("Your Container(s) list:\n")

        click.secho("ContainerID\tName\tStatus")
	
        idx = 1
        for i in result:
                if i['status'].upper() == 'RUNNING':
                        click.secho("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper(), fg='green')
                else:
                        click.secho("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper(), fg='red')
                        
                idx += 1
        print()

def stopContainer(authToken, url):

        serverAddress = url+"getUserContainers"
        header = dict()
        header['Authorization'] = authToken

        try:
                check = requests.get(serverAddress, headers=header)
        except:
                click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
                return

        result = json.loads(check.text)

        click.secho("ContainerID\tName\tStatus")

        idx = 1

        mp = {}

        for i in result:
                if(i['status'] == "running"):
                        mp[idx] = i['id']
                        click.secho("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper())
                        idx += 1

        idx -= 1
        if(idx == 0):
                click.secho("No containers available to stop\n", fg='red')
                return

        i = -1
        while True:
                click.secho("Enter the ID of the Container to stop: ")
                i = input()
                if(int(i)<=0 or int(i)>idx):
                        click.secho("Try again..", fg='red')
                else:
                        break

        data = dict()
        data['containerId'] = mp[int(i)]
        serverAddress = url+"stopContainer"
        try:
                check = requests.post(serverAddress, headers=header, json=data)
                result = json.loads(check.text)
                if(result['success']):
                        click.secho("The selected container has been successfully stopped..\n", fg='green')
                else:
                        click.secho("Something went wrong. Please try again later..\n", fg='red')
        except:
                click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
                return




def startContainer(authToken, url):

	serverAddress = url+"getUserContainers"
	header = dict()
	header['Authorization'] = authToken

	try:
		check = requests.get(serverAddress, headers=header)
	except:
		click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
		return

	result = json.loads(check.text)

	click.secho("Select the Container to stop:\n")
	click.secho("ContainerID\tName\tStatus")

	idx = 1

	mp = {}

	for i in result:
		if(i['status'] == "exited"):
			mp[idx] = i['id']
			click.secho("\t"+str(idx)+"\t"+i['name']+"\t"+i['status'].upper())
			idx += 1

	idx -= 1

	if(idx == 0):
		click.secho("All containers are already started.. No containers available to start..\n", fg='red')
		return

	i = -1
	while True:
		click.secho("Enter the ID of the Container to start: ")
		i = input()
		if(int(i)<=0 or int(i)>idx):
			click.secho("Try again..", fg='red')
		else:
			break

	data = dict()
	data['containerId'] = mp[int(i)]
	serverAddress = url+"startContainer"
	try:
		check = requests.post(serverAddress, headers=header, json=data)
		result = json.loads(check.text)
		if(result['success']):
			click.secho("The selected container has been successfully started..\n", fg='green')
		else:
			click.secho("Something went wrong. Please try again later..\n", fg='red')
	except:
		click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
		return




