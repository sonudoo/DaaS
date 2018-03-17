import docker
import os, sys
import images
from flask import jsonify

client = docker.from_env()
apiClient = docker.APIClient(base_url='unix://var/run/docker.sock')
dockerFilePath = "./"

def buildImage(username, password, containerImage):

    ubuntuDockerFileText = images.images[containerImage] % password
    dockerFile = open('Dockerfile', 'w')
    dockerFile.write(ubuntuDockerFileText.encode('utf8'))
    dockerFile.close()
    return client.images.build(path=dockerFilePath, tag="%s/ubuntu:%s" % (username, containerImage))


def runContainer(username, password, containerName, sudoPassword, containerImage, containerType):
    if containerType == '1':
        cpu = 1
        ram = '1g'
    else:
        cpu = 2
        ram = '2g'
    try:
        createdContainer =  client.containers.run(
            "%s/ubuntu:%s" % (username, containerImage),
            name=username+containerName,
            detach=True,
            ports={
                '22/tcp': None,
                '80/tcp': None
            },
            tty=True,
            cpu_count=cpu,
            mem_limit=ram
        )
    except Exception as error:
        print error
        return {
            'success': False,
            'error': str(error)
        }

    port_data = apiClient.inspect_container(createdContainer.id)['NetworkSettings']['Ports']

    ngnixFile = open('/etc/nginx/sites-available/default', 'r+')
    ngnixFileLines = ngnixFile.readlines()
    ngnixFileLines = ngnixFileLines[:-1]
    newLocation = [
        '\tlocation /%s/%s {\n' % (username, containerName),
		'\t\tproxy_pass http://localhost:%s/;\n' % port_data['80/tcp'][0]['HostPort'],
		'\t\tproxy_http_version 1.1;\n',
		'\t\tproxy_set_header Upgrade $http_upgrade;\n',
		"\t\tproxy_set_header Connection 'upgrade';\n",
		'\t\tproxy_set_header Host $host;\n',
		'\t\tproxy_cache_bypass $http_upgrade;\n',
    '\t}\n',
    '}'
    ]
    ngnixFileLines = ngnixFileLines + newLocation
    ngnixFile.seek(0)
    ngnixFile.writelines(ngnixFileLines)
    ngnixFile.truncate()
    ngnixFile.close()

    command = 'sudo nginx -s reload'
    print os.system('echo %s|sudo -S %s' % (sudoPassword, command))

    return {
        'success': True,
        'port22': port_data['22/tcp'][0]['HostPort'],
        'id': createdContainer.id
    }

def stopDockerContainer(containerId):
    try:
        container = client.containers.get(containerId)
        container.stop();
        return {
            "success": True
        }
    except Exception as e:
        print e
        return {
            "success": False
        }

def startDockerContainer(containerId):
    try:
        container = client.containers.get(containerId)
        container.start();
        return {
            "success": True
        }
    except Exception as e:
        print e
        return {
            "success": False
        }

def getStatus(id):
    return client.containers.get(id).status