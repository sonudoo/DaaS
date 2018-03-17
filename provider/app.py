from flask import Flask, jsonify, request
#from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
#from bson.json_util import dumps
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt_claims
from flask_cors import CORS
from dockerModule import buildImage, runContainer, stopDockerContainer, getStatus, startDockerContainer
import getpass
import socket

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
#mongo = PyMongo()
#bcrypt = Bcrypt()

CORS(app)

#mongo.init_app(app)
jwt = JWTManager(app)
#bcrypt.init_app(app)

sudoPassword = getpass.getpass()

@app.route('/createContainer', methods = ['POST'])
def createContainer():
    username = request.json['username']
    password = request.json['password']
    containerImage = request.json['containerImage']
    containerType = request.json['containerType']
    #print(buildImage(username, password, containerImage))
    container = runContainer(username, password, request.json['containerName'], sudoPassword, containerImage, containerType)

    print(container)
    
    if container['success']:
        try:
            return jsonify({
                'success': True,
                'port22': container['port22'],
                'port80': container['port80'],
                'containerId': container['id']
            })

        except Exception as e:
            print(e)
            return jsonify({
                'success': False,
                'msg': 'Something went wrong'
            })
    else:
        return jsonify(container)

@app.route('/stopContainer', methods=['POST'])

def stopContainer():
    containerId = request.json['containerId']
    result = stopDockerContainer(containerId)
    print(result)
    if(result['success']):
        return jsonify({
            "success": True
        })
    else:
        return jsonify({
            "success": False,
            "msg": "Something went wrong"
        })


@app.route('/startContainer', methods=['POST'])
def startContainer():

    containerId = request.json['containerId']
    try:
        result = startDockerContainer(containerId)
        return jsonify({
            "success": True
        })
    except:
        return jsonify({
            "success": False,
            "msg": 'Somthing went wrong'
        })

@app.route('/getContainerStatus', methods=['POST'])

def getContainerStatus():
    containerId = request.json['containerId']
    try:
        result = getStatus(containerId)
        return jsonify({
            "success": True,
            "status": result
        })
    except:
        return jsonify({
            "success": False,
            "msg": 'Somthing went wrong'
        })

if __name__ == '__main__':
    app.run(host = "192.168.43.230", port=3000, debug=True)