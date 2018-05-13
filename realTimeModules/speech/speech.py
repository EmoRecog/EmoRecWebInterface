import numpy as np
import time
from multiprocessing import Lock
import queue

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
    