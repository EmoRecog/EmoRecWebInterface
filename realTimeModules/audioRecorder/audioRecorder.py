import os
import pyaudio
import numpy as np
import pprint
import wave
import subprocess
import time

from .alsa_error import noalsaerr
from .channel_index import get_ip_device_index

import pickle
import pylab

def soundPlot(data):
    ROOT_AUDIORECORDERMODULE = os.path.dirname(os.path.realpath(__file__))
    ASSETSDIR = os.path.join(os.path.dirname(os.path.dirname(ROOT_AUDIORECORDERMODULE)),'static')
    WEBINTERFACE_AUD_PLOT = os.path.join(ASSETSDIR, 'plot.png')

    # print("SOUND PLOT -> path : " + WEBINTERFACE_AUD_PLOT)

    # print("SOUND PLOT -> data : {}".format(data))
    data = np.fromstring(data, dtype=np.int16)
    pylab.plot(data)
    # pylab.title(i)
    pylab.grid()
    pylab.axis([0,len(data),-2**16/2, 2**16/2])
    pylab.savefig(WEBINTERFACE_AUD_PLOT, dpi=50)
    pylab.close("all")

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
            # # for web interface
            soundPlot(streamData)
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

def readMic(utteranceToneQ,utteranceSpeechQ, audioInputDevice):
    
    # setup 
    DEVICE_IP_HW = audioInputDevice # this usually is hw:2,0
    # DEVICE_IP_HW = audioInput
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

        # THRESHOLD = getThreshold(stream, RATE, CHUNK, BASELINE_SECONDS) +3000 # just to be safe
        THRESHOLD = 20000 # set for testing
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
            
            utteranceToneQ.put(utteranceData)
            utteranceSpeechQ.put(utteranceData)
            # print("AUDIO RECORDER -> Utterance " + str(utteranceCount) + " recorded")
            # print("-----------------------------------------------")

            utteranceCount += 1

    except :
        pass

def readWavFile(utteranceToneQ,utteranceSpeechQ, audioInputFile):
    '''
    this reads 5 sec utterances from a file (THRESHOLD isn't used), 
    and passes on this utterances with 5 sec delay
    '''

    ROOT_AUDIORECORDERMODULE = os.path.dirname(os.path.realpath(__file__))
    PICKLESDIR = os.path.join(os.path.dirname(os.path.dirname(ROOT_AUDIORECORDERMODULE)),'picklesForInterface')
    WEBINTERFACE_AUD_OUTPUT =  os.path.join(PICKLESDIR, 'audioPickleFile')


    OUTPUT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test")
   
    # default parameters
    RATE = 16000
    CHUNK = 1024
    UTTERANCE_SECONDS = 5
    CHANNELS = 1

    try:
        MP4_FILE = audioInputFile
        FILE = MP4_FILE[:-4]
        print("FILE -> " + str(FILE))
    except :
        print("RECORDER -> NO AUDIO INPUT")


    print("Extracting audio from video : ", end= " ") # end=" " suppresses new line
    command = "ffmpeg -y -i " + MP4_FILE + " -ac 1 -ar 16000 -vn " + MP4_FILE[:-4] + ".wav"
    print(command)
    
    subprocess.call(command,shell=True)
    print("DONE")

    WAV_IN = audioInputFile[:-4]+".wav"
    testWav = wave.open(WAV_IN,"r")

    print("________________________________________")
    print("RECORDER -> READING FILE : " + WAV_IN)
    print("________________________________________")

    utteranceCount = 0
    while(True):
        try:           
            utterance = b'' # empty byte string
            # generate a 5 sec clip 
            for _ in range(int(RATE*UTTERANCE_SECONDS/CHUNK)):
                samples = testWav.readframes(CHUNK) # should throw error
                soundPlot(samples)
                if(len(samples)==0):
                    raise Exception("WAV FILE DONE")
                utterance += samples

            WAV_OUT  =os.path.join(OUTPUT_DIR,"wav_"+str(utteranceCount)+".wav")
            wavFile = wave.open(WAV_OUT, "w")
            wavFile.setnchannels(CHANNELS)
            wavFile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
            wavFile.setframerate(RATE)
            wavFile.writeframes(utterance)
            wavFile.close()

            print("RECORDER -> saved " + WAV_OUT)

            # handle exceptions for Qs separately, if needed
            # the 5 second delay should ensure the Q is emptied, though
            utteranceToneQ.put(utterance)
            utteranceSpeechQ.put(utterance)

            utteranceCount += 1
            
            # make processing sync with real time, deliberate delay of 5 seconds
            time.sleep(5)

        # except Queue.Full:
        #     print("QUEUE ERROR")

        except :
            break

def startAudioRecorder(utteranceToneQ,utteranceSpeechQ,audioInput):
    if(audioInput['input']=='mic'):
        readMic(utteranceToneQ, utteranceSpeechQ, audioInput['device'])
    
    if(audioInput['input']=='file'):
        readWavFile(utteranceToneQ, utteranceSpeechQ, audioInput['file'])
     

if __name__ == '__main__':
    # test()
    # startAudioRecorder()
    pass
