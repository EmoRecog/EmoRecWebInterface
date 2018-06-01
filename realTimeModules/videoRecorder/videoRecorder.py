from multiprocessing import Lock
import queue

import cv2
import time
import os

def startVideoRecorder(frameQ, videoInput):
    print("VIDEO RECORDER -> started")
    if(videoInput['input']=='camera'):
        videoInputSource = videoInput['device']
    
    if(videoInput['input']=='file'):
        videoInputSource = videoInput['file']
     

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


def main():
    pass