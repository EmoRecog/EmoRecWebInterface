from multiprocessing import Lock,Queue
import queue

import cv2
import time
import os

import socket
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
    
    videoInputIP = '0.0.0.0'
    videoInputPort = int(videoInput['port'])

    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    print('VIDEO RECORDER -> Socket created')
    print("VIDEO RECORDER -> Binding to IP : " + videoInputIP + ", Port : " + str(videoInputPort))

    s.bind((videoInputIP,videoInputPort))
    s.listen(5)

    conn,addr=s.accept()
    print("Connection from : " + str(conn))
    print("client addr : " + str(addr))

    frameCounter = 0

    while True:     
        data = ""
        while True:
            temp = conn.recv(4096)
            data += str(temp)
            if("END" in data):
                break
        
        temp = data[:-4] # remove END
        print(temp)

        temp = temp.split(" ")[:-1]
        frame = []
        for x in temp:
            if("b'" in x):
                # x = x[2:]
                x = x.decode("utf-8")
            print(x)    
            frame.append(int(x))


        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        print(frame)
        print(len(frame))
        print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")

        frame = np.fromstring(frame, dtype=np.uint8, sep = " ").reshape(480,640,3)
        
        # data = b""
        # payload_size = struct.calcsize("I") 
        # while True:
        #     while len(data) < payload_size:
        #         data += conn.recv(4096)
        #     packed_msg_size = data[:payload_size]
        #     data = data[payload_size:]
        #     msg_size = struct.unpack("I", packed_msg_size)[0]
        #     while len(data) < msg_size:
        #         data += conn.recv(4096)
        #     frame_data = data[:msg_size]
        #     data = data[msg_size:]
        #     ###

        # frame=pickle.loads(frame_data,encoding='bytes')
        # print(frame)
        
        
        
        # frameQ.put(frame)

        # cv2.imwrite(VIDEORECORDER_TESTDIR+"/stream.png",frame)
        
        cv2.imshow('stream',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
            break  
        
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