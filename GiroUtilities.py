__author__ = 'Cameron'
from datetime import datetime
from threading import Lock
import numpy as np
import urllib2

global logLock
logLock = Lock()

def log(myString):
    logLock.acquire()
    dt = datetime.now()
    time = (str(dt.hour) + ":" + str(dt.minute) + "." + str(dt.second) + "." + str(dt.microsecond).replace(' ', '')[:-3])
    while len(time) < 11:
        time += "0"
    print("ProjectGiro LOG " + time + ">\t" + str(myString))
    logLock.release()

#rewrite to accept fields parameter and return only the requested data
def pull_Yahoo_Finance_Data(symbol, dateRange):

        fileName = "StockData/"\
                   + symbol + ":"\
                   + dateRange["startM"]\
                   + "-" + dateRange["startD"]\
                   + "-" + dateRange["startY"]\
                   + "_" + dateRange["stopM"]\
                   + "-" + dateRange["stopD"]\
                   + "-" + dateRange["stopY"]\
                   + ".txt"

        log(fileName)

        try:
            f = open(fileName, "r")
            data = f.readlines()
            tempData = []
            log("Using stored data for " + symbol)
            for line in data:
                temp = line.rstrip()
                temp = temp.split(" ")
                tempDict = {}
                tempDict["date"] = temp[0]
                tempDict["open"] = np.double(temp[1])
                tempDict["high"] = np.double(temp[2])
                tempDict["low"] = np.double(temp[3])
                tempDict["close"] = np.double(temp[4])
                tempDict["volume"] = np.double(temp[5])
                tempData.append(tempDict)
            f.close()
            return tempData

        except:
            log("No stored data available for " + symbol)
            log("Pulling stock data for " + symbol + " from yahoo")

            base = "http://ichart.yahoo.com/table.csv?s="\
                   + symbol\
                   + "&a=" + dateRange["startM"]\
                   + "&b=" + dateRange["startD"]\
                   + "&c=" + dateRange["startY"]\
                   + "&d=" + dateRange["stopM"]\
                   + "&e=" + dateRange["stopD"]\
                   + "&f=" + dateRange["stopY"]\
                   + "&g=d&ignore=.cvs"

            log("Download URL: " + base)

            response = urllib2.urlopen(base)
            response = str(response.read())
            response = response.splitlines()
            response.pop(0)

            data = []
            for line in response:
                line = line.split(",")
                tempDict= {}
                tempDict["date"] = line[0]
                tempDict["open"] = np.double(line[1])
                tempDict["high"] = np.double(line[2])
                tempDict["low"] = np.double(line[3])
                tempDict["close"] = np.double(line[4])
                tempDict["volume"] = np.double(line[5])
                data.append(tempDict)
            data.reverse()

            log("Creating storage file for " + symbol)
            nf = open(fileName, 'w+')
            for dataPoint in data:
                nf.write(dataPoint["date"] + " " +
                         str(dataPoint["open"]) + " " +
                         str(dataPoint["high"]) + " " +
                         str(dataPoint["low"])+ " " +
                         str(dataPoint["low"]) + " " +
                         str(dataPoint["close"])+ " " +
                         str(dataPoint["volume"]) + "\n")
            nf.close()
            return data