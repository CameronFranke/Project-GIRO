__author__ = 'Cameron'
import time


def log(myString):
    currentTime = time.strftime("%H:%M.%S")
    print("ProjectGiro LOG " + str(currentTime) + ">\t" + str(myString))