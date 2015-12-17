__author__ = 'Cameron'
import LineageClass
import GiroUtilities as gu
import threading
import talib as tl
import numpy as np
global workerThreads
workerThreads = []
'''
TODO:

    get market averages as indicators
    dowJ = DJIA
    nasdaq composite = ^IXIC

'''

class GiroController():

    def __init__(self, resultsFile, stocksFile, configFile):
        self.configFile = configFile
        self.results = open(resultsFile, "w+")
        self.stocks = stocksFile
        self.settings = {}
        self.resultsLock = threading.Lock()
        self.stockQueueLock = threading.Lock()
        self.dateRange = {}
        self.nasdaq = []


    def init_stock_list(self):
        f = open(self.stocks, "r")
        f = f.readlines()
        temp = []
        for line in f:
            symbol = line.rstrip()
            temp.append(symbol)

        self.stocks = temp
        print self.stocks


    def get_settings(self):
        f = open(self.configFile, "r")
        temp = f.readlines()

        for line in temp:
            line = line.rstrip()
            line = line.split("=")
            self.settings[line[0]] = line[1]

        self.settings["threads"] = int(self.settings["threads"]) - 1


    def giro_start(self):
        global workerThreads

        gu.log("Initiating analysis of " + str(len(self.stocks)) + " securities")

        self.dateRange["startM"] = "00"
        self.dateRange["startD"] = "01"
        self.dateRange["startY"] = "2015"
        self.dateRange["stopM"] = "11"
        self.dateRange["stopD"] = "31"
        self.dateRange["stopY"] = "2015"

        for thread in range(self.settings["threads"]):
            workerThread = threading.Thread(target=self.start_worker, args=())
            workerThreads.append(workerThread)
            workerThread.start()

        for thread in workerThreads:
            thread.join()

        self.results.close()


    def start_worker(self):
        technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange", "RSI", "CCI", "volumeROCP", "chaikinAD", "nasdaqChange"]

        while True:
            self.stockQueueLock.acquire()
            if len(self.stocks) > 0:
                myStock = self.stocks.pop(0)
                self.stockQueueLock.release()
                x = (LineageClass.Lineage(myStock,
                                            self.dateRange,
                                            technicalIndicators,
                                            int(self.settings["populationSize"]),
                                            int(self.settings["generations"]),
                                            int(self.settings["lookbackLevel"]),
                                            float(self.settings["triggerThreshold"]),
                                            float(self.settings["dayTriggerThreshold"]),
                                            float(self.settings["selectionPercentage"]),
                                            float(self.settings["mutationRate"]),
                                            float(self.settings["mutationRateDelta"]),
                                            float(self.settings["startingMoney"]),
                                            float(self.settings["transactionCost"])))

                x.master_initialize()

                print x.data ############################

                recommendation = x.evolve()
                self.resultsLock.acquire()
                self.results.write(myStock + ": " + recommendation + "\n")
                self.resultsLock.release()

            else:
                self.stockQueueLock.release()
                break