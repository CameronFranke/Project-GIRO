__author__ = 'Cameron'
import LineageClass
import GiroUtilities as gu
import multiprocessing
import threading
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
        self.resultsFile = open(resultsFile, "w+")
        self.resultStrings = ""
        self.stocks = stocksFile
        self.settings = {}
        self.resultsLock = threading.Lock()
        self.stockQueueLock = threading.Lock()
        self.dateRange = {}
        self.nasdaq = []
        self.manager = multiprocessing.Manager()


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

        self.settings["threads"] = int(self.settings["threads"])


    def giro_start(self):
        global workerThreads

        gu.log("Initiating analysis of " + str(len(self.stocks)) + " securities")

        self.dateRange["startM"] = "00"
        self.dateRange["startD"] = "01"
        self.dateRange["startY"] = "2015"
        self.dateRange["stopM"] = "11"
        self.dateRange["stopD"] = "31"
        self.dateRange["stopY"] = "2015"

        self.stocks = self.manager.list(self.stocks)
        self.resultStrings = self.manager.list()



        mylock = multiprocessing.Lock()
        for thread in range(self.settings["threads"]):
            workerThread = multiprocessing.Process(target=self.start_worker, args=(mylock,))
            workerThreads.append(workerThread)
            workerThread.start()

        for thread in workerThreads:
            thread.join()

        for line in self.resultStrings:
            self.resultsFile.write(line)
        self.resultsFile.close()


    def start_worker(self, lock):
        technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange", "RSI", "CCI", "volumeROCP", "chaikinAD", "nasdaqChange"]

        while True:
            lock.acquire()
            if len(self.stocks) > 0:
                myStock = self.stocks.pop(0)
                lock.release()
                x = (LineageClass.Lineage(myStock,
                                            self.dateRange,
                                            technicalIndicators,
                                            self.settings))

                x.master_initialize()
                recommendation = x.evolve()
                self.resultStrings.append(str(myStock + ": " + recommendation + "\n"))

            else:
                lock.release()
                break