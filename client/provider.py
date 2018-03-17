import requests, json, click, multiprocessing, os

def registerAsProvider(authToken, url):
	serverAddress = url+"registerHoster"
	data = dict()
	while True:
		print("There are two types of instances:\n1. 1 vCPUs, 1 GB RAM\n2. 2 vCPUs, 2 GB RAM\n")
		print("Enter number of instances of first type that you are ready to allot: ")
		type1 = input()
		print("Enter number of instances of second type that you are ready to allot: ")
		type2 = input()
		mem_usage = int(type1)+int(type2)*2
		mem_avail = (os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES'))/(1024**3)
		processor_usage = int(type1)+int(type2)*2
		processor_avail = multiprocessing.cpu_count()
		if(mem_avail < mem_usage or processor_avail < processor_usage):
			print("Selected configuration surpasses the system available resources. Try again..")
		else:
			data['type1'] = type1
			data['type2'] = type2
			break
	
	try:
		header = dict()
		header['Authorization'] = authToken
		check = requests.post(serverAddress, headers=header, json=data)
		result = json.loads(check.text)
		if(result['success']):
			print('Congratulations! You have sucessfully been registered as a Hoster.\n')
		else:
			print('You are already registered as a Hoster.\n')
	except:
		click.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
		returnclick.secho("Connection Error: Make sure that the server is reachable..\n", fg='red')
	return