import os
import pickle
import queue  # multiprocessing.Queue borrows exceptions from Queue
import time
from multiprocessing import Process, Queue

import numpy as np

from speech.speech import generateSpeechProbs
from tone.tone import generateToneProbs, detectEmotionsTone
from video.video import detectEmotionsVideo, generateVideoProbs
from audioRecorder.audioRecorder import startAudioRecorder

#TODO: clamp weight values between 0 and 1
# for testing

def majorityVotedEmotion(videoProbs, toneProbs, speechProbs, weights = None):
    # None is used just to handle conditions at t = 0s
    weightedAvgProbs = None
    majorityVote = None
    try:
        probs = np.concatenate((videoProbs, toneProbs, speechProbs)).reshape(3,-1)
        weightedAvgProbs = np.average(probs, axis=0, weights=weights)
        majorityVote = np.argmax(weightedAvgProbs)
    except:
        # for any exceptions thrown, just pass
        pass

    return majorityVote, weightedAvgProbs

def main():
    #init paths
    ROOT_INTERFACE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ROOT_REALTIMEMODULES = os.path.dirname(os.path.realpath(__file__))
    VIDEO = os.path.join(ROOT_REALTIMEMODULES, "video")
    VIDEO_TEST = os.path.join(VIDEO,"test")
    TONE = os.path.join(ROOT_REALTIMEMODULES, "tone")
    TONE_TEST = os.path.join(TONE, "test")
    SPEECH = os.path.join(ROOT_REALTIMEMODULES, "speech")
    SPEECH_TEST = os.path.join(SPEECH, "test")
    PICKLES = os.path.join(ROOT_INTERFACE, "picklesForInterface")

    # spawn 3 processes which are asynchronous
    # each has an infinite loop
    videoProbs = None
    toneProbs = None
    speechProbs = None

    videoProbUpdate = False
    toneProbUpdate = False
    speechProbUpdate = False

    videoWeight = 0.0
    toneWeight = 0.0
    speechWeight = 0.0

    videoProbQ = Queue()
    toneProbQ = Queue()
    speechProbQ = Queue()
    utteranceQ = Queue()

    videoAttrQ = Queue()
    toneAttrQ = Queue()
    speechAttrQ = Queue()
    # Last 2 are for future use

    # videoProcess = Process(target=generateVideoProbs, args=(videoProbQ,))
    videoProcess = Process(target=detectEmotionsVideo, args=(videoProbQ, videoAttrQ,os.path.join(ROOT_REALTIMEMODULES, "video", "test","videoplayback.mp4")))
    # toneProcess = Process(target=generateToneProbs, args=(toneProbQ,))
    toneProcess = Process(target=detectEmotionsTone, args=(toneProbQ, toneAttrQ, utteranceQ))
    speechProcess = Process(target=generateSpeechProbs, args=(speechProbQ,))
    audioRecorderProcess = Process(target=startAudioRecorder, args=(utteranceQ,))

    videoProcess.start()
    toneProcess.start()
    speechProcess.start()
    audioRecorderProcess.start()

    #default values
    videoAttrs = 0 


    counter = 0
    # use a scheduler here if you want the function call at specified time
    # or use wall time with time.sleep (refer to bookmarks : stackover timer)
    while(True):
        # separate try-except blocks needed because, if one of the generateProbs 
        # doesn't generate a new value, we still need the rest to be updated
        # if all the generateProbs calls are in one try block, try block will 
        # throw exception at the first empty queue it encounters and rest of the 
        # probs won't be updated
        try:
            # if there is no data in the queue, it means classifier hasn't 
            # updated it yet, for new input. it will throw an exception, which 
            # is caught in except block, where we reduce weight of this classifier
            videoProbs = videoProbQ.get(block=False)
            
            # Everytime a fresh update occurs, the weight for classifier is set to 1
            # Other parameters for weight increments can be considered here
            # such as the frame contrast etc.
            videoProbUpdate = True
            videoWeight = 1.0

            # Retrieve the video attributes : frameNo and emotionLabel
            # For no updates, videoAttrs will have old values, be sure not to print those
            videoAttrs = videoAttrQ.get()
        except queue.Empty:
            # If classifier doesn't update, we reduce the weight
            # Other parameters for weight reduction can be considered here
            videoProbUpdate = False
            videoWeight -= 0.2

            
        try:
            toneProbs = toneProbQ.get(block=False)
            toneProbUpdate = True
            toneWeight = 1.0
            toneAttrs = toneAttrQ.get()
        except queue.Empty:
            toneProbUpdate = False
            toneWeight -= 0.2
        try:
            speechProbs = toneProbQ.get(block=False)
            speechProbUpdate = True
            speechWeight = 1.0
        except queue.Empty:
            speechProbUpdate = False
            speechWeight -= 0.2


        print("Probabilities at -> " + str(counter) + " seconds")      
        print("Video Probs : UPDATE : " + str(videoProbUpdate))
        if(videoProbUpdate):
            print("Frame no : " + str(videoAttrs[0]) + ", EmotionLabel : " + str(videoAttrs[1]))
        print(videoProbs)
        
        print("Tone Probs : UPDATE : " + str(toneProbUpdate))
        if(toneProbUpdate):
            print("Utterance no : " + str(toneAttrs[0]) + ", Emotion Label : " + str(toneAttrs[1]))
        print(toneProbs)
        
        print("Speech Probs : UPDATE : " + str(speechProbUpdate))
        print(speechProbs)
        
        weights = [videoWeight, toneWeight, speechWeight]
        emotion, weightedAvgProbs = majorityVotedEmotion(videoProbs, toneProbs, speechProbs, weights)
        print("Majority Voted Emotion : " + str(emotion))
        print("Weights : ") 
        print(weights)
        print("Probs : ")
        print(weightedAvgProbs)
        print("\n")

        transmitArray = [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs,  videoAttrs] 
        with open(os.path.join(PICKLES,'pickleFile'), 'wb') as fp:
                    pickle.dump(transmitArray, fp)


        # the video module processes more than 1 frame per second, 
        # so, for this delay, we get an update in videoProbs for each second
        # remove this time.sleep(1) call to see 'no update' in video module

        # time.sleep(0) should be zero for final code
        time.sleep(1)
        counter += 1


if __name__=="__main__":
    main()
