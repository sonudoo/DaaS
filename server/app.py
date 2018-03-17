from flask import Flask, jsonify, request
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from bson.json_util import dumps
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt_claims
from flask_cors import CORS
from dockerModule import buildImage, runContainer
import getpass

app = Flask(__name__)
app.config.from_pyfile('config.cfg')
mongo = PyMongo()
bcrypt = Bcrypt()

CORS(app)

mongo.init_app(app)
jwt = JWTManager(app)
bcrypt.init_app(app)

sudoPassword = getpass.getpass()

@app.route("/login", methods=['POST'])
def login():
    print "sdkjfn"
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
    containerType = request.json['containerType']
    print buildImage(username, password, containerType)
    container = runContainer(username, password, request.json['containerName'], sudoPassword, containerType)
    print container
    if container['success']:
        try:
            containerCollection = mongo.db.containers
            containerCollection.insert({
                "id": container['id'],
                "name": request.json['containerName'],
                "username": username
            })

            return jsonify({
                'success': True,
                'ssh': 'ssh -p ' + container['port22'] + ' root@192.168.43.93'
            })

        except Exception as e:
            print e
            return jsonify({
                'success': False,
                'msg': 'Something went wrong'
            })
    else:
        return jsonify(container)

@app.route('/getUserContainers')
@jwt_required
def getUserContainers():
    username = get_jwt_identity()
    containerCollection = mongo.db.containers
    containerList = containerCollection.find({'username': username})
    return dumps(containerList)


if __name__ == '__main__':
    app.run(host = '192.168.43.93', port=3000, debug = True)