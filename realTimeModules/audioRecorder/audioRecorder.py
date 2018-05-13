import os
import pyaudio
import numpy as np
import pprint
import wave

from .alsa_error import noalsaerr
from .channel_index import get_ip_device_index

def getThreshold(stream, RATE, CHUNK, BASELINE_SECONDS):
    maxChunks = []
    for i in range(0,int(RATE/CHUNK*BASELINE_SECONDS)):
        streamData = stream.read(CHUNK)
        streamData = np.fromstring(streamData, np.int16)
        maxChunks.append(np.max(streamData))
    maxChunks = np.array(maxChunks)
    # print(maxChunks)
    THRESHOLD = np.mean(maxChunks)
    return THRESHOLD

def isSilent(audioChunk, THRESHOLD):
    '''
    Returns 'True' if below the 'silent' threshold
    takes audioChunk which is a binary string
    (audioChunk is converted to np array here, do no pre-convert it)
    '''
    audioChunk = np.fromstring(audioChunk, np.int16)
    # print("MAX : " + str(np.max(audioChunk)))
    return np.max(audioChunk) < THRESHOLD

def getUtterance(stream, RATE, CHUNK, THRESHOLD, CHECK_SILENCE_SECONDS, RECORD_SECONDS):
    # record audio of CHECK_SILENCE_SECONDS
    utteranceData = b''    
    count = 0 # keep track of 1-sec clips added to the utterance
    while(True):
        checkData = b''
        for _ in range(int(RATE*CHECK_SILENCE_SECONDS/CHUNK)):
            streamData = stream.read(CHUNK)
            checkData += streamData
        
        if(isSilent(checkData, THRESHOLD)):
            print("RECORDER -> Silence")
            utteranceData = b'' # wipe the previous 1-second audios
            count = 0
            print("RECORDER -> Discarded previous clips")
            continue
        else:
            utteranceData += checkData
            print("RECORDER -> Added clip " + str(count))
            count += 1
            if(count >5):
                print("RECORDER -> Returning generated utterance ")
                break
        
    return utteranceData

def test():

    # setup 
    DEVICE_IP_HW = "Camera" # this usually is hw:2,0
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 4096
    BASELINE_SECONDS = 3
    CHECK_SILENCE_SECONDS = 1
    RECORD_SECONDS = 5
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test")

    with noalsaerr():
        p = pyaudio.PyAudio() # start the PyAudio class

    # open stream with this device
    stream = p.open(format=FORMAT, channels=CHANNELS,rate=RATE,input_device_index=get_ip_device_index(p, DEVICE_IP_HW), input=True,
                    frames_per_buffer=CHUNK)

    

    THRESHOLD = getThreshold(stream, RATE, CHUNK, BASELINE_SECONDS) +3000 # just to be safe
    print("THRESHOLD : " + str(THRESHOLD))

    utterance = 0
    while(True):
        utteranceData = getUtterance(stream, RATE, CHUNK, 
                                THRESHOLD, CHECK_SILENCE_SECONDS, RECORD_SECONDS)
      
        # set up the wav container 
        wavFile = wave.open(os.path.join(OUTPUT_DIR, "mic_" + str(utterance) + ".wav"), "w")
        wavFile.setnchannels(1)
        wavFile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
        wavFile.setframerate(16000)
        wavFile.writeframes(utteranceData)
        wavFile.close()
        print("saved " + os.path.join(OUTPUT_DIR, "mic_" + str(utterance) + ".wav"))
        utterance += 1


    # close the stream 
    wavFile.close()
    stream.stop_stream()
    stream.close()
    p.terminate()

def startAudioRecorder(utteranceQ):
    # setup 
    DEVICE_IP_HW = "Camera" # this usually is hw:2,0
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 4096
    BASELINE_SECONDS = 3
    CHECK_SILENCE_SECONDS = 1
    UTTERANCE_SECONDS = 5
    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test")

    try:
        with noalsaerr():
            p = pyaudio.PyAudio() # start the PyAudio class

        # open stream with this device
        stream = p.open(format=FORMAT, channels=CHANNELS,rate=RATE,input_device_index=get_ip_device_index(p, DEVICE_IP_HW), input=True,
                        frames_per_buffer=CHUNK)

        THRESHOLD = getThreshold(stream, RATE, CHUNK, BASELINE_SECONDS) +3000 # just to be safe
        print("________________________________________")
        print("RECORDER -> Threshold : " + str(THRESHOLD))
        print("________________________________________")

        utteranceCount = 0
        while(True):
            utteranceData = getUtterance(stream, RATE, CHUNK, 
                                    THRESHOLD, CHECK_SILENCE_SECONDS, UTTERANCE_SECONDS)
            # print("-----------------------------------------------")
            # set up the wav container to store the recorded 5 second utterances
            wavFile = wave.open(os.path.join(OUTPUT_DIR, "mic_" + str(utteranceCount) + ".wav"), "w")
            wavFile.setnchannels(CHANNELS)
            wavFile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wavFile.setframerate(RATE)
            wavFile.writeframes(utteranceData)
            wavFile.close()
            # print("saved " + os.path.join(OUTPUT_DIR, "mic_" + str(utteranceCOunt) + ".wav"))
            
            utteranceQ.put(utteranceData)
            # print("AUDIO RECORDER -> Utterance " + str(utteranceCount) + " recorded")
            # print("-----------------------------------------------")

            utteranceCount += 1

    except :
        pass
   
     

if __name__ == '__main__':
    # test()
    startAudioRecorder()