from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.json_util import dumps
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt_claims
from flask_cors import CORS
from dockerModule import buildImage, runContainer, stopDockerContainer, getStatus, startDockerContainer
from userCreation import createUser
import getpass
import requests
import socket
import json
import os, sys

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mongo = PyMongo()
bcrypt = Bcrypt()
serverIp = '192.168.43.93'

CORS(app)

try:
    mongo.init_app(app)
except Exception as e:
    print e

jwt = JWTManager(app)
bcrypt.init_app(app)

sudoPassword = getpass.getpass()

@app.route("/login", methods=['POST'])
def login():
    try:
        username = request.json['username']
        password = request.json['password']
        userCollection = mongo.db.users
        user = userCollection.find_one({'username': username})
        if user and password == user['password']:
            access_token = create_access_token(identity=username)
            return jsonify({
                "success": True,
                "token": 'Bearer '+ access_token
            })
        else:
            return jsonify({"success": False, "msg": "Invalid username or password"})
    except Exception as e:
        print e
        return jsonify({"success": False, "msg": "Something went wrong"})

@app.route("/register", methods = ['POST'])
def register():
    print "reached register"
    try:
        userCollection = mongo.db.users
        user = userCollection.find_one({'username': request.json['username']})
        if user:
            return jsonify({'success': False, 'msg': 'Username already exists'})
        else:
            userCollection.insert(request.json)
            return jsonify({'success': True, 'msg': 'Successfully Registered'})
    except Exception as e:
        print 'Error while registering user: ' + str(e)
        return jsonify({'success': False, 'msg': 'Something went wrong'})


@app.route('/createContainer', methods = ['POST'])
@jwt_required
def createContainer():
    username = get_jwt_identity()
    userCollection = mongo.db.users
    password = userCollection.find_one({'username': username})['password']
    containerImage = request.json['containerImage']
    containerType = request.json['containerType']
    hostsCollection = mongo.db.hosts
    hostsList = hostsCollection.find({})


    for host in hostsList: 
        if (containerType == '1' and int(host['type1']) > 0) or (containerType == '2' and int(host['type2']) > 0):
            postData = {
                "username": username,
                "containerName": request.json['containerName'],
                "containerImage": request.json['containerImage'],
                "containerType": request.json['containerType'],
                "password": password
            }
            address = 'http://'+host['ip']+':3000/createContainer'
            print address
            try:
                port = requests.post(address, json=postData)
            except Exception as e:
                print e
            print port.text
            result = json.loads(port.text)
            if result['success']:
                containerCollection = mongo.db.containers
                containerCollection.insert({
                    "id": result['containerId'],
                    "ip": host['ip'],
                    "name": request.json['containerName'],
                    "username": username
                })
                ngnixFile = open('/etc/nginx/sites-available/default', 'r+')
                ngnixFileLines = ngnixFile.readlines()
                ngnixFileLines = ngnixFileLines[:-1]
                newLocation = [
                    '\tlocation /%s/%s {\n' % (username, request.json['containerName'],),
                    '\t\tproxy_pass http://%s:%s/;\n' % (host['ip'], result['port80']),
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
            
                if int(host['type1']) > 0:
                    hostsCollection.update_one({"_id": host["_id"]}, {"$set": {"type1": int(host['type1']) - 1}})
                elif int(host['type2']) > 0:
                    hostsCollection.update_one({"_id": host["_id"]}, {"$set": {"type2": int(host['type1']) - 1}})
                
                return jsonify({
                'success': True,
                'ssh': 'ssh -p ' + result['port22'] + ' root@%s' % host['ip']
                })

            else: 
                continue

    print buildImage(username, password, containerImage)
    container = runContainer(username, password, request.json['containerName'], sudoPassword, containerImage, containerType)
    if container['success']:
        try:
            containerCollection = mongo.db.containers
            containerCollection.insert({
                "id": container['id'],
                "ip": serverIp,
                "name": request.json['containerName'],
                "username": username
            })
            return jsonify({
                'success': True,
                'ssh': 'ssh -p ' + container['port22'] + ' root@%s' %serverIp
            
            })

        except Exception as e:
            print e
            return jsonify({
                'success': False,
                'msg': 'Something went wrong'
            })
    else:
        return jsonify(container)

@app.route('/stopContainer', methods=['POST'])
@jwt_required
def stopContainer():
    username = get_jwt_identity()
    containerId = request.json['containerId']
    containerCollection = mongo.db.containers
    query = containerCollection.find_one({'username': username, 'id': containerId})
    if query:
        if query['ip'] == serverIp:
            result = stopDockerContainer(containerId)
            if result["success"]:
                return jsonify({
                    "success": True,
                    "msg": 'Successfully stopped container %s' % query['name']
                })
            else:
                return jsonify({
                    "success": False,
                    "msg": 'Somthing went wrong'
                })
        else:
            postData = {
                "containerId": containerId
            }
            result = requests.post('http://'+query['ip']+':3000/stopContainer', json=postData)
            print result.text
            result = json.loads(result.text)
            if result['success']:
                return jsonify({
                    "success": True,
                    "msg": 'Successfully stopped container %s' % query['name']
                })
            else:
                return jsonify({
                    "success": False,
                    "msg": 'Somthing went wrong'
                })
    else:
        return jsonify({
            "success": False,
            "msg": 'Container not found!'
        })

@app.route('/startContainer', methods=['POST'])
@jwt_required
def startContainer():
    username = get_jwt_identity()
    containerId = request.json['containerId']
    containerCollection = mongo.db.containers
    query = containerCollection.find_one({'username': username, 'id': containerId})
    if query:
        if query['ip'] == serverIp:
            result = startDockerContainer(containerId)
            if result["success"]:
                return jsonify({
                    "success": True,
                    "msg": 'Successfully stopped container %s' % query['name']
                })
            else:
                return jsonify({
                    "success": False,
                    "msg": 'Somthing went wrong'
                })
        else:
            postData = {
                "containerId": containerId
            }
            result = requests.post('http://'+query['ip']+':3000/startContainer', json=postData)
            print result.text
            result = json.loads(result.text)
            if result['success']:
                return jsonify({
                    "success": True,
                    "msg": 'Successfully stopped container %s' % query['name']
                })
            else:
                return jsonify({
                    "success": False,
                    "msg": 'Somthing went wrong'
                })
    else:
        return jsonify({
            "success": False,
            "msg": 'Container not found!'
        })



@app.route('/getUserContainers')
@jwt_required
def getUserContainers():
    username = get_jwt_identity()
    containerCollection = mongo.db.containers
    containerList = containerCollection.find({'username': username})
    userContainers = [];
    for item in containerList:
        if item['ip'] == serverIp:
            containerStatus = getStatus(item['id'])
            userContainers.append({
                "name": item['name'],
                "id": item['id'],
                "status": containerStatus
            })
        else:
            postData = {
                "containerId": item['id']
            }
            result = requests.post('http://'+item['ip']+':3000/getContainerStatus', json=postData)
            result = json.loads(result.text)
            if result['success']:
                userContainers.append({
                "name": item['name'],
                "id": item['id'],
                "status": result['status']
                });
    return jsonify(userContainers)

@app.route('/registerHoster', methods=['POST'])
@jwt_required
def registerHoster():
    username = get_jwt_identity()
    hostsCollection = mongo.db.hosts
    host = hostsCollection.find_one({"username": username})
    if host:
        return jsonify({
            "success": False,
            "msg": "User already registered"
        })
    else:
        try: 
            hostsCollection.insert({
                "username": username,
                "ip": request.remote_addr,
                "type1": request.json['type1'],
                "type2": request.json['type2']
            })
            return jsonify({
                "success": True,
                "msg": "Successfully registed user"
            })
        except Exception as e:
            print e
            return jsonify({
                "success": False,
                "msg": "Something went wrong"
            })

@app.route('/createDatabase', methods=['POST'])
@jwt_required
def createDatabase():
    username = get_jwt_identity()
    userCollection = mongo.db.users
    password = userCollection.find_one({'username': username})['password']
    databaseName = request.json['databaseName']
    return jsonify(createUser(username, password, databaseName))
    



if __name__ == '__main__':
    app.run(host = serverIp, port=3000, debug = True, threaded=True)