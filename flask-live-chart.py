import json
from time import time
from random import random
from flask import Flask, render_template, make_response
import os
import pickle

#readFile = 'faceRecog/testfile'     #format : [a, d, h, n, sad, sur, frame]
# //format : [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs, videoAttrs, toneAttrs]
# // size :  [    4                3           6       4           4              2       2       ]

app = Flask(__name__)
ROOT_INTERFACE = os.path.dirname(os.path.realpath(__file__))
readFile = os.path.join(ROOT_INTERFACE, 'picklesForInterface','pickleFile')

@app.route('/')
def renderHomePage():
    return render_template('index.html', data = 'test')

@app.route('/videoPage')
def renderVideoPage():
    return render_template('videoPage.html', data = 'test')

@app.route('/audioPage')
def renderAudioPage():
    return render_template('audioPage.html', data = 'test')

@app.route('/textPage')
def renderTextPage():
    return render_template('textPage.html', data = 'test')

#reads data from pipe file and sends to javaScript Highcharts
@app.route('/live-data')
def live_data():
 
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

# app.run(debug=True, host='127.0.0.1', port=5000)
app.run(debug=True, host='0.0.0.0', port=5000)