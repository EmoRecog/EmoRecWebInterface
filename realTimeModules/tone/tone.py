import glob
import os
import pprint
import queue
import subprocess
import sys
import time
import wave
from multiprocessing import Lock

import numpy as np
import pandas as pd
import pyaudio
from sklearn.externals import joblib

from .energy import getTopEnergySegmentsIndices
from .featureExtraction import extractFeatures, getSegmentFeaturesUsingIndices


def generateToneProbs(toneProbQ):
    lock = Lock()
    randomGenerator = np.random.RandomState(seed=2)
    while(True):
        lock.acquire()
        try:
            toneProbs = randomGenerator.rand(6)
            toneProbQ.put(toneProbs, block=False)
        except queue.Full:
            pass
        finally:
            lock.release()
        time.sleep(6)

def detectEmotionsTone(toneProbQ, toneAttrQ, utteranceQ):
    lock = Lock()
    while(True):
        lock.acquire()
        try:
            # set module root
            DIR = os.path.dirname(os.path.realpath(__file__))

            # set up wav container parameters
            CHANNELS = 1
            RATE = 16000
            SAMPLEWIDTH = 2

            # read utterance from utteranceQ
            emotions = ['neu','sad_fea', 'ang_fru','hap_exc_sur']

            # setup 
            OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test")

            # load models
            scaler = joblib.load(DIR + "/scalerParameters.sav")
            dnn = joblib.load(DIR  + "/dnnParameters.sav")

            utteranceCount = 0
            while(True):
                # get utterance from the audioRecorder
                utteranceData = utteranceQ.get()
                
                # set up the wav container to store the recorded 5 second utterances
                wavFile = wave.open(os.path.join(OUTPUT_DIR, "mic_" + str(utteranceCount) + ".wav"), "w")
                wavFile.setnchannels(CHANNELS)
                wavFile.setsampwidth(SAMPLEWIDTH)
                wavFile.setframerate(RATE)
                wavFile.writeframes(utteranceData)
                wavFile.close()
                # print("saved " + os.path.join(OUTPUT_DIR, "mic_" + str(utteranceCOunt) + ".wav"))
                
                print("TONE -> Utterance " + str(utteranceCount) + " recorded")

                utterance = np.fromstring(utteranceData, np.int16)
                frameFeatureMatrix = extractFeatures(utterance, RATE)
                topSegmentIndices = getTopEnergySegmentsIndices(utterance, RATE)
                topSegmentFeatureMatrix = getSegmentFeaturesUsingIndices(frameFeatureMatrix, 25, topSegmentIndices)

                # normalize data
                topSegmentFeatureMatrix = scaler.transform(topSegmentFeatureMatrix)
                # generate probabilities with DNN
                segmentProbabilities = dnn.predict_proba(topSegmentFeatureMatrix)
                # create high level features
                avgSegmentProbabilities = np.mean(segmentProbabilities, axis=0)                
                # determine emotionLabelNum
                emotionLabelNum = np.argmax(avgSegmentProbabilities)

                # generate toneProbsQ here
                # TODO : test, remove this later
                print("----------------------------")
                print(avgSegmentProbabilities)
                print("----------------------------")
                toneAttrs = [utteranceCount, emotions[emotionLabelNum]]
                toneAttrQ.put(toneAttrs)
                toneProbQ.put(avgSegmentProbabilities)

                utteranceCount += 1

        except queue.Full:
            pass
        finally:
            lock.release()
    pass