import numpy as np
import time
from multiprocessing import Lock
import queue

import cv2
import dlib
from sklearn.svm import SVC
from sklearn.externals import joblib
import math
import os

def generateVideoProbs(videoProbQ):
    # Ensure that when generateVideoProbs is generating values,
    # videoProbs wont be used in the main program
    lock = Lock()       
    randomGenerator = np.random.RandomState(seed=1)
    while(True):
        lock.acquire()
        try:
            videoProbs = randomGenerator.rand(6)
            videoProbQ.put(videoProbs, block=False)
        except queue.Full:
            pass
        finally:
            lock.release()
        time.sleep(3)

def get_landmarks(image, detector, predictor):

    data = {}
    detections = detector(image, 1)
    for k,d in enumerate(detections): #For all detected face instances individually
        shape = predictor(image, d) #Draw Facial Landmarks with the predictor class
        xlist = []
        ylist = []
        for i in range(1,68): #Store X and Y coordinates in two lists
            xlist.append(float(shape.part(i).x))
            ylist.append(float(shape.part(i).y))
            
        xmean = np.mean(xlist)
        ymean = np.mean(ylist)
        xcentral = [(x-xmean) for x in xlist]
        ycentral = [(y-ymean) for y in ylist]

        landmarks_vectorised = []
        for x, y, w, z in zip(xcentral, ycentral, xlist, ylist):
            landmarks_vectorised.append(w)
            landmarks_vectorised.append(z)
            meannp = np.asarray((ymean,xmean))
            coornp = np.asarray((z,w))
            dist = np.linalg.norm(coornp-meannp)
            landmarks_vectorised.append(dist)
            landmarks_vectorised.append((math.atan2(y, x)*360)/(2*math.pi))

        data['landmarks_vectorised'] = landmarks_vectorised
    if len(detections) < 1: 
        data['landmarks_vectorised'] = "error"
    return data 

# For later
def getVideoInput(s):
    try:
        return int(s)
    except ValueError:
        return s

def detectEmotionsVideo(videoProbQ, videoAttrQ, videoInput):

    #init root directory path
    ROOT_VIDEOMODULE = os.path.dirname(os.path.realpath(__file__))

    WEBINTERFACE_VID_OUTPUT = os.path.join(os.path.dirname(os.path.dirname(ROOT_VIDEOMODULE)), 'static', 'video.png')

    # print("VIDEO -> videoInput : " + videoInput)
    emotions = ["anger","disgust", "happiness", "neutral", "sadness", "surprise"] #Emotion list

    # dlib's face detector, required for get_landmarks
    detector = dlib.get_frontal_face_detector()     
    
    # TODO Change haar's cascaded clf to HOG clf from dlib
    faceDet = cv2.CascadeClassifier(ROOT_VIDEOMODULE + "/haarcascade_frontalface_default.xml")
    faceDet_two = cv2.CascadeClassifier(ROOT_VIDEOMODULE + "/haarcascade_frontalface_alt2.xml")
    faceDet_three = cv2.CascadeClassifier(ROOT_VIDEOMODULE + "/haarcascade_frontalface_alt.xml")
    faceDet_four = cv2.CascadeClassifier(ROOT_VIDEOMODULE + "/haarcascade_frontalface_alt_tree.xml")

    # to get the landmarks
    predictor = dlib.shape_predictor(ROOT_VIDEOMODULE + "/shape_predictor_68_face_landmarks.dat")

    # emotion detector
    clf = joblib.load(ROOT_VIDEOMODULE + "/EmoRecogFacial.pkl")
    
    skipframe=48
    # try:
    #     skipframe = int(sys.argv[2])
    # except ValueError:
    #     pass
    
    video_capture = cv2.VideoCapture(videoInput)
    # video_capture = cv2.VideoCapture(2)

    proc_frame = np.zeros((350,350,3), np.uint8)
    counter = 0
    

    while(True):
        

        counter += 1
        ret, orig_frame = video_capture.read()
        
        if ret == False:
            break
        
        if( counter % skipframe == 0):
            frame = orig_frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            face = faceDet.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face_two = faceDet_two.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face_three = faceDet_three.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            face_four = faceDet_four.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5), flags=cv2.CASCADE_SCALE_IMAGE)
            
            if len(face) == 1:
                facefeatures = face
            elif len(face_two) == 1:
                facefeatures = face_two
            elif len(face_three) == 1:
                facefeatures = face_three
            elif len(face_four) == 1:
                facefeatures = face_four
            else:
                facefeatures = ""

            for (x, y, w, h) in facefeatures: #get coordinates and size of rectangle containing face
                frame = frame[y:y+h, x:x+w] #Cut the frame to size
                #CHECK IF RESIZING IS NEEDED
                try:
                    frame = cv2.resize(frame, (350, 350)) #Resize face so all images have same size
                except:
                    pass #If error, pass file


            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            clahe_image = clahe.apply(frame)

            data = get_landmarks(clahe_image, detector, predictor)

            if data['landmarks_vectorised'] == "error":
                print("VIDEO -> No face detected")
            else:
                pred = []
                pred.append(data['landmarks_vectorised'])
                npar = np.array(pred)
                dist = clf.decision_function(npar)
                result = emotions[clf.predict(npar)[0]]
                prob = clf.predict_proba(npar) * 100
                # print("dist : " + str(dist))
                # print("VIDEO -> prob : " + str(prob) + "%")
                # print("VIDEO -> frame : " + str(counter/skipframe) + ", emotion : " + result)

                ''' 
                Sending the data  to main process
                ---------------------------------
                '''
                videoProbs = prob[0]
                videoProbQ.put(videoProbs)

                frameNo =counter/skipframe
                emotionLabel = result
                videoAttrs = [frameNo, emotionLabel]
                videoAttrQ.put(videoAttrs)
                '''
                ----------------------------------
                '''

            proc_frame = frame
            cv2.putText(proc_frame, "frame : "+str(counter/skipframe), (30,30), cv2.FONT_HERSHEY_PLAIN, 1.5, 255)
            
        # TODO: show these outputs in the webinterface  video module
        time.sleep(1/float(35))
        cv2.imshow("original_feed", orig_frame) #Display the frame
        
        # saving output for dashboard display
        resized_frame = cv2.resize(orig_frame, (200,150))
        cv2.imwrite(WEBINTERFACE_VID_OUTPUT, resized_frame)
    

        cv2.imshow("processed_feed", proc_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): #Exit program when the user presses 'q'
            break        

        # TESTING asynchronous playback
        # ret, image = video_capture.read()
        # cv2.imshow("video", image)
        # if (cv2.waitKey(1) & 0xFF == ord('q')):
        #     break

# test   
# detectEmotionsVideo(None, "videoplayback.mp4")
