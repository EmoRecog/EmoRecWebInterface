import numpy as np
import time
from multiprocessing import Lock
import queue

def generateToneProbs(toneProbQ):
    lock = Lock()
    randomGenerator = np.random.RandomState(seed=2)
    while(True):
        lock.acquire()
        try:
            toneProbs = randomGenerator.rand(6)
            toneProbQ.put(toneProbs, block=False)
        except queue.Full:
            pass
        finally:
            lock.release()
        time.sleep(6)
    