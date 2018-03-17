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
    dockerFile.write(ubuntuDockerFileText)
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
            #"%s/ubuntu:%s" % (username, containerImage),
            "sus-blank:latest",
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
        return {
            'success': False,
            'error': str(error)
        }

    port_data = apiClient.inspect_container(createdContainer.id)['NetworkSettings']['Ports']

    return {
        'success': True,
        'port22': port_data['22/tcp'][0]['HostPort'],
        'port80': port_data['80/tcp'][0]['HostPort'],
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
        print(e)
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
        print(e)
        return {
            "success": False
        }

def getStatus(id):
    return client.containers.get(id).status