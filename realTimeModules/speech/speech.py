# TODO : results skewed towards anger, possible solution, balance dataset for training

import io
import os
import pickle
import queue
import threading
import time
from multiprocessing import Lock
import time

import numpy as np
from google.cloud import speech
from google.cloud.speech import enums, types
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB

ROOT_SPEECHMODULE = os.path.dirname(os.path.realpath(__file__))

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.path.join(ROOT_SPEECHMODULE, 'api_key.json')

def generateSpeechProbs(speechProbQ):
    lock = Lock()
    randomGenerator = np.random.RandomState(seed=3)
    while(True):
        lock.acquire()
        try:
            speechProbs = randomGenerator.rand(4) 
            speechProbQ.put(speechProbs, block=False)
        except queue.Full:
            pass
        finally:
            lock.release()
        time.sleep(5)

class Classifier():

    def __init__(self, target_names, count_vect, tfidf_transformer, classifier):
        self.target_names = target_names
        self.count_vect = count_vect
        self.tfidf_transformer = tfidf_transformer
        self.classifier = classifier

    def predict(self, data):
        X_new_counts = self.count_vect.transform(data)
        X_new_tfidf = self.tfidf_transformer.transform(X_new_counts)
        predicted =  self.classifier.predict(X_new_tfidf)
        return [self.target_names[p] for p in predicted]
    
    def predict_proba(self, data):
        X_new_counts = self.count_vect.transform(data)
        X_new_tfidf = self.tfidf_transformer.transform(X_new_counts)
        return self.classifier.predict_proba(X_new_tfidf)

def train():

    target_names = ['neu', 'sad', 'ang', 'hap']
    targets = []
    data = []

    with open(os.path.join(ROOT_SPEECHMODULE, 'transcriptions.tsv'), 'r') as fp:
        for line in fp:
            arr = line.split('\t')
            #if(arr[1] not in target_names):
            #    target_names.append(arr[1])
            #targets.append(target_names.index(arr[1]))
            if(arr[1] in ['neu']):
                targets.append(0)
            elif(arr[1] in ['sad','fea']):
                targets.append(1)
            elif(arr[1] in ['ang','fru']):
                targets.append(2)
            elif(arr[1] in ['hap','exc','sup']):
                targets.append(3)
            else:
                continue            
            data.append(arr[2])
		
    count_vect = CountVectorizer()
    X_train_counts = count_vect.fit_transform(data)
    print(X_train_counts.shape)

    tfidf_transformer = TfidfTransformer()
    X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
    print(X_train_tfidf.shape)

    clf = MultinomialNB().fit(X_train_tfidf, targets)

    classifier = Classifier(target_names, count_vect, tfidf_transformer, clf)

    with open(os.path.join(ROOT_SPEECHMODULE, 'savefile'), 'wb') as savefile:
        pickle.dump(classifier, savefile, pickle.HIGHEST_PROTOCOL)

    return classifier

def loadClassifier():

    if(os.path.exists(os.path.join(ROOT_SPEECHMODULE, 'savefile'))):
        with open(os.path.join(ROOT_SPEECHMODULE, 'savefile'), 'rb') as savefile:
            classifier = pickle.load(savefile)
    else:
        classifier = train()

    return classifier # tempTranscript = []
            # for t in transcript:
            #     if (time.time()-t[1] < 25.0):
            #         tempTranscript.append(t)            
            # transcript = tempTranscript

def getWeight(wordcount):
	return 0.6 + 0.4 * min(1, 0.01 * 0.05 * wordcount * wordcount)


def detectEmotionsSpeech(speechProbQ, speechAttrQ, utteranceSpeechQ):
    target_names = ['neu', 'sad_fea', 'ang_fru_dis', 'hap_exc_sur']

    client = speech.SpeechClient()
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')
    streaming_config = types.StreamingRecognitionConfig(config=config)
    classifier = loadClassifier()
    lock = Lock()
    utteranceCount = 0
    transcript = []

    while(True):
        lock.acquire()
        try:
            
            content = utteranceSpeechQ.get()
            print("SPEECH -> Recorded utterance audio " + str(utteranceCount), len(content))
            requests = (types.StreamingRecognizeRequest(audio_content=chunk) for chunk in [content])
            responses = client.streaming_recognize(streaming_config, requests)
            
            for response in responses:
                for result in response.results:
                    for alternative in result.alternatives:
                        transcript.append((alternative.transcript, time.time()))

            transcript = [t for t in transcript if ((time.time() - t[1]) < 25.0) ]
            # tempTranscript = []
            # for t in transcript:
            #     if (time.time()-t[1] < 25.0):
            #         tempTranscript.append(t)            
            # transcript = tempTranscript

            # if no transcript is received, continue with old paragraph (with previous transcripts) until paragraph is flushed
            if(transcript):
                emoProbs = classifier.predict_proba([' '.join([t[0] for t in transcript])])[0]
                speechAttrs = [ ' '.join([t[0] for t in transcript]), target_names[np.argmax(emoProbs)], getWeight(len(' '.join([t[0] for t in transcript]).split(' '))) ] 
                
                speechAttrQ.put(speechAttrs)
                speechProbQ.put(emoProbs*100)
                
                
            #utteranceCount+=1
            # flush out the paragraph after every 6 utterances
            #if(utteranceCount % 6 == 0):
            #    transcript = ''

        except queue.Full:
            pass
        finally:
            lock.release()
