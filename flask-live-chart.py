import json
from time import time
from random import random
from flask import Flask, render_template, make_response
import os
import pickle

app = Flask(__name__)
#readFile = 'faceRecog/testfile'     #format : [a, d, h, n, sad, sur, frame]

#format : [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs,    videoAttr         ]
# size :  [    6                3           6       6           6             2  ]
readFile = os.path.join(os.path.realpath(__file__), 'CombiningProbs', 'picklefile')

@app.route('/')
def renderHomePage():
    return render_template('index.html', data='test')

@app.route('/live-data')
def live_data():
    '''
    with open(readFile, 'rb') as fp:
        receivedData = pickle.load(fp)
        print('Received data is : ',receivedData)
    '''
    with open(readFile, 'rb') as fp:
        pickeDump = pickle.load(fp)
    receivedData = []
    #convert to single 1D array
    for array in pickeDump:
        for element in array:
            receivedData.append(element)

    response = make_response(json.dumps(receivedData))
    response.content_type = 'application/json'
    return response

app.run(debug=True, host='127.0.0.1', port=5000)
