__author__ = 'Cameron'
from datetime import datetime
from threading import Lock

global logLock
logLock = Lock()

def log(myString):
    logLock.acquire()
    dt = datetime.now()
    time = (str(dt.hour) + ":" + str(dt.minute) + "." + str(dt.second) + "." + str(dt.microsecond).replace(' ', '')[:-3])
    print("ProjectGiro LOG " + time + ">\t" + str(myString))
    logLock.release()