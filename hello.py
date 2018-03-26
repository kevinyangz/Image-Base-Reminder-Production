from cloudant import Cloudant
from flask import Flask, render_template, request, jsonify,Response,redirect,url_for
import atexit
import cf_deployment_tracker
import os
import json
import jsonpickle


import sys
import logging
from flask_uploads import UploadSet, configure_uploads, IMAGES
from testInceptionV3 import get_model_api
from freshnessBanana import get_freshness_model
from flask_cors import CORS
import time
import numpy as np
import cv2



# Emit Bluemix deployment event
cf_deployment_tracker.track()

app = Flask(__name__)

db_name = 'mydb'
client = None
db = None
CORS(app) # needed for cross-domain requests, allow everything by default

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

# logging for heroku
if 'DYNO' in os.environ:
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)


# load the model
model_api = get_model_api()
#model_api=None
freshness_api= get_freshness_model()


if 'VCAP_SERVICES' in os.environ:
    vcap = json.loads(os.getenv('VCAP_SERVICES'))
    print('Found VCAP_SERVICES')
    if 'cloudantNoSQLDB' in vcap:
        creds = vcap['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)
elif os.path.isfile('vcap-local.json'):
    with open('vcap-local.json') as f:
        vcap = json.load(f)
        print('Found local VCAP_SERVICES')
        creds = vcap['services']['cloudantNoSQLDB'][0]['credentials']
        user = creds['username']
        password = creds['password']
        url = 'https://' + creds['host']
        client = Cloudant(user, password, url=url, connect=True)
        db = client.create_database(db_name, throw_on_exists=False)

# On Bluemix, get the port number from the environment variable PORT
# When running this app on the local machine, default the port to 8000
port = int(os.getenv('PORT', 8000))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.files['files[]'].filename == '':
            return redirect(url_for('home'))

    if request.method == 'POST' and 'files[]' in request.files:
        files = request.files.getlist("files[]")
        listresult=[]
        for filename in files:
            filename = photos.save(filename)
            filename='static/img/'+filename
           
            if(model_api):
                start=time.time()
                result =model_api(filename,False)
                freshness_result=freshness_api(filename)
                end=round(time.time()-start,2)
                list=result.split(':')
                category=list[0]
                confidence=list[1]
                #print(freshness_result)
                list2=freshness_result.split(':')
                label=list2[0]
                confidence_label=list2[1]
                date=list2[2]
                dictr = {'category': category, 'confidence': confidence, 'duration': end,'filename':filename,'fresh':label,'freshcon':confidence_label,'date':date}
                listresult.append(dictr)

            else:
                #fake result
                dictr = {'category': "fake apple", 'confidence': "100%", 'duration': 12345,'filename':filename,'fresh':"Fake",'date':2}
                print (dictr)
                listresult.append(dictr)
        size=len(listresult)
        gridresult=""
        if(size%4 is 0):
            gridresult="col-md-3 col-sm-6 col-xs-12"
        elif(size %3 is 0):
            gridresult="col-md-4 col-sm-4 col-xs-12"
        elif(size%2 is 0):
            gridresult="col-md-6 col-sm-6 col-xs-12"
        elif(size is 1):
          gridresult="col-md-%s col-sm-%s col-xs-12"%(int(12/size),int(12/size))
        else:
          gridresult="col-md-3 col-sm-6 col-xs-12"
        return render_template('index.html',datas=listresult,grid=gridresult)
    
    #print ("debug Messages:"+filename)
    return render_template('simple_client.html')

@app.route('/')
def home():
    return render_template('simple_client.html')

# /* Endpoint to greet and add a new visitor to database.
# * Send a POST request to localhost:8000/api/visitors with body
# * {
# *     "name": "Bob"
# * }
# */
@app.route('/api/visitors', methods=['GET'])
def get_visitor():
    if client:
        return jsonify(list(map(lambda doc: doc['name'], db)))
    else:
        print('No database')
        return jsonify([])

@app.route('/api/test', methods=['POST'])
def test():
    start=time.time()
    r = request
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    result =model_api(img,True)
    # do some fancy processing here....
    end=round(time.time()-start,1)
    # build a response dict to send back to client
    response = {'message': result+"time: "+str(end)+"seconds"}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")



# /**
#  * Endpoint to get a JSON array of all the visitors in the database
#  * REST API example:
#  * <code>
#  * GET http://localhost:8000/api/visitors
#  * </code>
#  *
#  * Response:
#  * [ "Bob", "Jane" ]
#  * @return An array of all the visitor names
#  */
@app.route('/api/visitors', methods=['POST'])
def put_visitor():
    user = request.json['name']
    if client:
        data = {'name':user}
        db.create_document(data)
        return 'Hello %s! I added you to the database.' % user
    else:
        print('No database')
        return 'Hello %s!' % user

@atexit.register
def shutdown():
    if client:
        client.disconnect()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=False)
