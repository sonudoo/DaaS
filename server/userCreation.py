from pymongo import MongoClient

client = MongoClient('localhost:27017')   
client.admin.authenticate('admin', 'pass')


def createUser(username, password, databaseName):
    dnames = client.database_names()
    if databaseName in dnames:
        return {
            "success": False,
            "msg": 'Database already exists!'
        }
    try:
        db = client[databaseName]
        db.add_user(username, password, roles=[{'role':'readWrite','db':databaseName}])
        db.authenticate(username, password)
        db.users.insert_one({"username": "test", "password": "test"})
        return {
            "success": True,
            "msg": 'Successfully created'
        }
    except Exception as e:
        print e
        return {
            "success": False,
            "msg": 'Something went wrong'
        }
