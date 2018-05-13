import numpy as np
from python_speech_features import mfcc
import scipy.io.wavfile as wavfile
from .energy import getTopEnergySegmentsIndices
import os
import sys

def extractFeatures(audio, audioRate):
    '''
    returns an matrix of mfccs per each 25 ms frame,sliding with 10 ms 
    '''
    # default window length is 0.025 seconds and sliding rate is 0.010 seconds
    mfccMatrix = mfcc(audio, audioRate)
    # normalize the features in the matrix
    mu = np.mean(mfccMatrix, axis=0)
    sigma = np.std(mfccMatrix, axis=0)
    mfccMatrix = (mfccMatrix - mu) / sigma
    return mfccMatrix

def getSegmentFeaturesUsingIndices(mfccMatrix, numberOfFramesPerSegment, indicesTopEnergySegments):
    '''
    generates features for segments from the frames in that segment
    return a new matrix [indexofTopSegment -> segmentFeatureMatrix : MFCCs of 25 frames in that segment]
    '''
    # Note : index of a segment is nothing but the index of the starting frame of that segment
    segmentFeatureMatrix = mfccMatrix

    for rotationIndex in range(numberOfFramesPerSegment-1): # hstack the rotated matrix 24 times
        rotatedMfccMatrix = np.vstack([mfccMatrix[(rotationIndex+1):,:], mfccMatrix[0:(rotationIndex+1),:]])
        segmentFeatureMatrix = np.hstack([ segmentFeatureMatrix, rotatedMfccMatrix ])

    # now we have segmentFeatureMatrix, in which every row holds the (13 MFCCs/frame * 25 frames) = 325 features 
    # for each segment, we need only those segments whose energy is in top 10 percent. 
    # return an ndarray of only those segments using the indicesTopEnergySegments
    topSegmentFeatureMatrix = segmentFeatureMatrix[indicesTopEnergySegments, :]
    return topSegmentFeatureMatrix


def main():
    debug = True
    # get an audio file
    audioRate, audio = wavfile.read(os.path.dirname(os.path.realpath(__file__)) + "/wavs/pyaudio_record.wav")

    mfccMatrix = extractFeatures(audio, audioRate)
    if(debug):
        print("MFCCs per each frame : ")
        for frame in range(len(mfccMatrix)):
            print("frame #" + str(frame) + " -> " + str(mfccMatrix[frame,:]))
            ''' Note that each segment has 13 MFCCs'''

    indicesTopEnergySegments = getTopEnergySegmentsIndices(audio, audioRate)
    if(debug):
        print("indices of 10% top energy segments : ") 
        print(indicesTopEnergySegments)
        print("Number of top segments : ") 
        print(len(indicesTopEnergySegments))
    
    topSegmentFeatureMatrix = getSegmentFeaturesUsingIndices(mfccMatrix,25,indicesTopEnergySegments)
    if(debug):
        # print the first segment feature vector as a test
        print("segment feature vecor -> number of features : " + str(len(topSegmentFeatureMatrix[0])))
        print(topSegmentFeatureMatrix[0])
    

if __name__ == '__main__':
    main()