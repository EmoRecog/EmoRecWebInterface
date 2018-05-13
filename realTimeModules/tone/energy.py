import sys
import scipy.io.wavfile as wavfile
import numpy as np
import os

def getTopEnergySegmentsIndices(signal,
                      signalRate = 16000, 
                      segmentDurationSeconds = 0.265, # segment of 265 milliseconds
                      segmentShiftSeconds = 0.010, # segment shift of 10 milliseconds
                      percentage = 0.10,  # 10% of the segment to be considered
                      debug = False):
    '''
    Returns index of 10 % of the frames in the sentence, energy-wise
    '''

    origDatatype = type(signal[0])
    if debug:
        print("origDatatype ->")
        print(origDatatype)

    # get the machine limits for this int type
    typeInfo = np.iinfo(origDatatype)
    if debug:
        print("typeInfo ->")
        print(str(typeInfo))
    isUnsigned = typeInfo.min >= 0
    if debug:
        print("isUnigned ->")
        print(isUnsigned)

    # signal ndarray contains samples -> signed integers 2 bytes wide, 
    # dtype originally is np.int16. For calculations, we convert it to 
    # np.int64
    signal = signal.astype(np.int64)


    if isUnsigned:
        signal = signal - (typeinfo.max + 1) / 2

    signalSamples = len(signal)
    # signal is ndarray of samples, signalRate is samples/second
    # to get segments of 265 milliseconds, we need signalRate * frameDuration=0.265
    # here segmentSamples refers to number of samples in segment
    # similarly, segmentShiftSamples refers to number of samples by which segment is shifted
    segmentSamples = int(signalRate * segmentDurationSeconds)
    segmentShiftSamples = int(signalRate * segmentShiftSeconds)

    i = 0
    segmentEnergyList = []
    while (i+segmentSamples) < signalSamples:
        segmentData = signal[i:i+segmentSamples]
        segmentEnergy = np.sum(segmentData**2) / float(len(segmentData))
        segmentEnergyList.append(segmentEnergy)
        i += segmentShiftSamples

    segmentEnergyNDarray = np.array(segmentEnergyList)
    totalSegments = len(segmentEnergyNDarray)
    topSegments = int(totalSegments * percentage)

    # we need the indices of top (percentage) segments energy-wise, 
    # sorted in descending order
    # argsort()returns indices such that elements taken with those indices 
    # give the sorted array. We take only last totalSegments, which are the 
    # top energy segments. 
    # We reverse the list, as we need then in descending order

    indicesOfTopSegmentsPerSignal = segmentEnergyNDarray.argsort()[-topSegments:][::-1]
    return indicesOfTopSegmentsPerSignal

def main():
    audioSignalRate, audioSignal = wavfile.read(os.path.dirname(os.path.realpath(__file__)) + "/wavs/pyaudio_record.wav")
    print("indices : " + str(getTopEnergySegmentsIndices(audioSignal, audioSignalRate)))


if __name__ == '__main__':
    main()