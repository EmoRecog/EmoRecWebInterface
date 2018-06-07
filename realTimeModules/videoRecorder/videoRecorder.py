from multiprocessing import Lock,Queue
import queue

import cv2
import time
import os

from socket import *
import pickle
import struct
import numpy as np

def localVideoRecorder(frameQ, videoInputSource):
    #init root directory path
    ROOT_VIDEORECORDERMODULE = os.path.dirname(os.path.realpath(__file__))
    WEBINTERFACE_VID_OUTPUT = os.path.join(os.path.dirname(os.path.dirname(ROOT_VIDEORECORDERMODULE)), 'static', 'video.png')
    VIDEORECORDER_TESTDIR = os.path.join(ROOT_VIDEORECORDERMODULE, 'test')

    # detemine 'n'th frame to be processed
    skipframe=48

    try:
        videoInputSource = int(videoInputSource)
    except ValueError:
        pass

    video_capture = cv2.VideoCapture(videoInputSource)

    frameCounter = 0
    while(True):
        ret, frame = video_capture.read()
        if ret == False:
            print("VIDEO RECORDER -> no video input")
            break

        if(frameCounter % skipframe == 0):
            frameQ.put(frame)


        cv2.putText(frame, "frame : "+str(frameCounter), (30,30), cv2.FONT_HERSHEY_PLAIN, 1.5, 255)

        time.sleep(1/float(35))

        # display frame
        cv2.imshow("feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
            break  
        cv2.imwrite(VIDEORECORDER_TESTDIR+"/frame.png", frame)

        # saving output for dashboard display
        resized_frame = cv2.resize(frame, (200,150))
        cv2.imwrite(WEBINTERFACE_VID_OUTPUT, resized_frame)
    
        frameCounter += 1

def remoteStream(frameQ, videoInput):
    # init root directory path
    ROOT_VIDEORECORDERMODULE = os.path.dirname(os.path.realpath(__file__))
    WEBINTERFACE_VID_OUTPUT = os.path.join(os.path.dirname(os.path.dirname(ROOT_VIDEORECORDERMODULE)), 'static', 'video.png')
    VIDEORECORDER_TESTDIR = os.path.join(ROOT_VIDEORECORDERMODULE, 'test')
    
    # videoInputIP = '127.0.0.1'
    videoInputIP = '0.0.0.0'
    videoInputPort = int(videoInput['port'])

    skipframe = 10
    frameCounter = 0

    while True:     
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind((videoInputIP, videoInputPort))
        # print("VIDEO RECORDER -> SOCKET bind at {}:{}".format(videoInputIP,videoInputPort))
        
        f = open(os.path.join(VIDEORECORDER_TESTDIR,"streamImg.jpg"), "wb")
        data, address = s.recvfrom(1024)
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        # print("VIDEO RECORDER -> address : {}".format(address)) 
        # print(data)
        # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")


        try:
            while(data):
                f.write(data)
                s.settimeout(0.05)
                data, address = s.recvfrom(1024)
                # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                # print("VIDEO RECORDER -> address : {}".format(address)) 
                # print(data)
                # print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        except timeout:
            f.close()
            s.close()
        
        frame = cv2.imread(os.path.join(VIDEORECORDER_TESTDIR,"streamImg.jpg"))

        if(frameCounter % skipframe == 0):
            frameQ.put(frame)

        # saving output for dashboard display
        resized_frame = cv2.resize(frame, (200,150))
        cv2.imwrite(WEBINTERFACE_VID_OUTPUT, resized_frame)

        try:
            cv2.imshow('stream',frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
                break
        except : 
            pass  
        
        frameCounter += 1

def startVideoRecorder(frameQ, videoInput):

    print("VIDEO RECORDER -> started")
    if(videoInput['input']=='camera'):
        localVideoRecorder(frameQ, videoInput['device'])

    if(videoInput['input']=='file'):
        localVideoRecorder(frameQ, videoInput['file'])
     
    if(videoInput['input']=='stream'):
        remoteStream(frameQ, videoInput)

def main():
    frameQ = Queue()
    videoInput = {'input':'stream','port':8089}
    remoteStream(frameQ, videoInput)


if __name__ == '__main__':
    main()