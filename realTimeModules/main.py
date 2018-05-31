import os
import pickle
import queue  # multiprocessing.Queue borrows exceptions from Queue
import time
import sys
import argparse
from multiprocessing import Process, Queue


import numpy as np

from speech.speech import generateSpeechProbs, detectEmotionsSpeech
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
    emotions = ['neu','sad_fea', 'ang_fru','hap_exc_sur']
    
    #init paths
    ROOT_INTERFACE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ROOT_REALTIMEMODULES = os.path.dirname(os.path.realpath(__file__))
    TESTVIDEOS_DIR = os.path.join(ROOT_INTERFACE, "testVideos")
    
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
    combinedVideoProbs = None
    toneProbs = None
    speechProbs = None

    videoProbUpdate = False
    toneProbUpdate = False
    speechProbUpdate = False

    videoWeight = 0
    toneWeight = 0
    speechWeight = 0

    videoProbQ = Queue()
    toneProbQ = Queue()
    speechProbQ = Queue()
    utteranceToneQ = Queue()
    utteranceSpeechQ = Queue()

    videoAttrQ = Queue()
    toneAttrQ = Queue()
    speechAttrQ = Queue()

    
    # parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--file","-f",help="name of the file, in testVideos")
    parser.add_argument("--camera","-c",help="index of camera device")
    parser.add_argument("--mic", "-m", help="name of the mic device")
    parser.add_argument_group()

    if(len(sys.argv)<2):
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()
    
    if(args.file):
        print(args.file)
        videoProcess = Process(target=detectEmotionsVideo, args=(videoProbQ, videoAttrQ,os.path.join(TESTVIDEOS_DIR, args.file+".mp4")))
        audioInput = {'input':'file', 'file':os.path.join(TESTVIDEOS_DIR, args.file+".mp4")}
        audioRecorderProcess = Process(target=startAudioRecorder, args=(utteranceToneQ, utteranceSpeechQ, audioInput))

    
    if(args.mic or args.camera):
        if(args.mic and args.camera):
            print("camera : " + args.camera)
            print("Mic : " + args.mic)
            videoProcess = Process(target=detectEmotionsVideo, args=(videoProbQ, videoAttrQ,args.camera))
            audioInput = {'input':'mic','device':args.mic}

            audioRecorderProcess = Process(target=startAudioRecorder, args=(utteranceToneQ, utteranceSpeechQ,  audioInput))
        else:
            print("Input mic and camera!")


    # videoProcess = Process(target=generateVideoProbs, args=(videoProbQ,))
    # TODO handle mp4 and avi
    # videoProcess = Process(target=detectEmotionsVideo, args=(videoProbQ, videoAttrQ,os.path.join(TESTVIDEOS_DIR, sys.argv[1]+".mp4")))
    # toneProcess = Process(target=generateToneProbs, args=(toneProbQ,))
    toneProcess = Process(target=detectEmotionsTone, args=(toneProbQ, toneAttrQ, utteranceToneQ))
    # speechProcess = Process(target=generateSpeechProbs, args=(speechProbQ,))
    speechProcess = Process(target=detectEmotionsSpeech, args=(speechProbQ, speechAttrQ, utteranceSpeechQ))
    # audioRecorderProcess = Process(target=startAudioRecorder, args=(utteranceToneQ, utteranceSpeechQ,  os.path.join(TESTVIDEOS_DIR, sys.argv[1]+".mp4")))

    videoProcess.start()
    toneProcess.start()
    speechProcess.start()
    audioRecorderProcess.start()

    #default values, each will return two values : [Frame/utterence/transcription , emotionLabel]
    videoAttrs = 0
    toneAttrs = 0
    speechAttrs = 0

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
            combinedVideoProbs = np.array([videoProbs[3],   # neu
                                            videoProbs[4],  # sad_fea
                                            videoProbs[0]+videoProbs[1], # ang_fru_dis
                                            videoProbs[2]+videoProbs[5]]) # hap_exc_sur
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
            if videoWeight >= 0.2:
                videoWeight -= 0.2

            
        try:
            toneProbs = toneProbQ.get(block=False)
            toneProbUpdate = True
            # toneProbs = np.zeros(6) + 50
            toneWeight = 1.0
            toneAttrs = toneAttrQ.get()
        except queue.Empty:
            toneProbUpdate = False
            if toneWeight >= 0.2:
                toneWeight -= 0.2
        try:
            # TODO refresh weight later, hacked together now
            speechProbs = speechProbQ.get(block=False)
            speechProbUpdate = True
            # speechWeight = 1.0
            speechWeight = 0.2
            speechAttrs = speechAttrQ.get()
        except queue.Empty:
            speechProbUpdate = False
            # if speechWeight >= 0.2:
            #     speechWeight -= 0.2
            if speechWeight >= 0.04:
                speechWeight -= 0.04


        print("Probabilities at -> " + str(counter) + " seconds")      
        print("Video Probs : UPDATE : " + str(videoProbUpdate))
        if(videoProbUpdate):
            print("Frame no : " + str(videoAttrs[0]) + ", EmotionLabel : " + str(videoAttrs[1]))
        print("Video Probs : " + str(videoProbs))
        print("Combined video probs : " + str(combinedVideoProbs))
        
        print("Tone Probs : UPDATE : " + str(toneProbUpdate))
        if(toneProbUpdate):
            print("Utterance no : " + str(toneAttrs[0]) + ", Emotion Label : " + str(toneAttrs[1]))
        print("Tone probs : " + str(toneProbs))
        
        print("Speech Probs : UPDATE : " + str(speechProbUpdate))
        if(speechProbUpdate):
            print("Transcript : " + str(speechAttrs[0]))
            print("Emotion Label : "+ str(speechAttrs[1]))
        print("Speech probs : " + str(speechProbs))
        
        weights = [videoWeight, toneWeight, speechWeight]
        emotion, weightedAvgProbs = majorityVotedEmotion(combinedVideoProbs, toneProbs, speechProbs, weights)
        print("Majority Voted Emotion : " + str(emotion))
        print("Weights : ", end = "") 
        print(weights)
        print("WEIGHTED Probs : ", end = "")
        print(weightedAvgProbs)
        print("\n")
        
        # comparison data
        print("**********************************")
        print("VIDEO_EMOTION : " + str(np.argmax(combinedVideoProbs)))
        print("TONE_EMOTION : " + str(np.argmax(toneProbs)))
        print("SPEECH_EMOTION : " + str(np.argmax(speechProbs)))
        print("MAJORITY_EMOTION : " + str(np.argmax(weightedAvgProbs)))
        print("**********************************")


        # covering for the hack written in speech weight update
        # correct display on console, fake display on web interface
        weights[2] *= 5

        transmitArray = [weightedAvgProbs, weights, videoProbs, toneProbs, speechProbs,  videoAttrs, toneAttrs, speechAttrs] 
        arrayGood = True
        for x in transmitArray:
            if x is None:
                arrayGood = False
        if arrayGood:
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
