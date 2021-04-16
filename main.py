from google.cloud import datastore
from flask import Flask, request, make_response
import json
import constants

# This disables the requirement to use HTTPS so that you can test locally.
import os 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
client = datastore.Client()

#allows for debugging in VS code.
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, True)

file = open("client_secret.json", 'r')
clientData = file.read()
jsonString = json.loads(clientData)
clientID = jsonString['web']['client_id']
clientSecret = jsonString['web']['client_secret']
redirectURI = jsonString['web']['redirect_uris'][0]
scope = 'https://www.googleapis.com/auth/userinfo.profile'
app.secret_key = clientSecret


@app.route('/')
def index():
    return "Please navigate to /boats to use this API"



#assigns the self variable
def create_self(item):
    selfURL = request.base_url + '/' + str(item.id)
    item["self"] = selfURL
    return item

def create_self_second(item):
    item["self"] = request.base_url
    return item

#takes in list of results and returns a bool if key exists or not.
def check_ID_existence(results, id):
    for object in results:
        if id == 'null':
            break
        if object.id == int(id):
            return True #id is in
    return False


@app.route('/boats', methods=['POST','GET'])
def boats_get_or_post():
    if request.method == 'POST':
        content = request.get_json()
        if (not(content)): #if could not get the content in json format
            return(constants.jsonOnlyAcceptJson, 415)
        if ("name" not in content or "type" not in content or "length" not in content or "public" not in content):
            return (constants.jsonErrorStringArgs, 400)
        query = client.query(kind=constants.boats) #load the boats
        results = list(query.fetch()) #store boats into a list
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({"name": content["name"], "type": content["type"],
        "length": content["length"], "public": content["public"], "owner": content["owner"]})
        client.put(new_boat)
        new_boat["id"] = new_boat.id
        create_self(new_boat)
        return (new_boat, 201)
    
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        jsonData = json.dumps(results)
        return (jsonData, 200)
    else:
        return 'Method not recogonized'

@app.route('/owners/<ownid>/boats', methods=['GET'])
def owner_boats(ownid):
    pass

@app.route('/boats/<bid>', methods=['DELETE'])
def delete_boat(bid):
    pass

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
    
    
