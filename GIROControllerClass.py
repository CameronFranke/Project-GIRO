__author__ = 'Cameron'
import LineageClass
import GiroUtilities as gu
import multiprocessing
import threading
from operator import itemgetter

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
        self.results = ""
        self.stocks = stocksFile
        self.settings = {}
        self.resultsLock = threading.Lock()
        self.stockQueueLock = threading.Lock()
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


    def get_settings(self):
        f = open(self.configFile, "r")
        temp = f.readlines()

        for line in temp:
            line = line.rstrip()
            line = line.split("=")
            self.settings[line[0]] = line[1]

        self.settings["threads"] = int(self.settings["threads"])

        for key in self.settings:
            gu.log(key + "=" + str(self.settings[key]))


    def giro_start(self):
        global workerThreads

        gu.log("Initiating analysis of " + str(len(self.stocks)) + " securities")
        self.stocks = self.manager.list(self.stocks)
        self.results = self.manager.list()

        mylock = multiprocessing.Lock()
        for thread in range(self.settings["threads"]):
            workerThread = multiprocessing.Process(target=self.start_worker, args=(mylock,))
            workerThreads.append(workerThread)
            workerThread.start()

        for thread in workerThreads:
            thread.join()

        self.results = sorted(self.results, key=itemgetter(2))
        self.results.reverse()

        totalRecs = 0
        incorrectRecs = 0
        for line in self.results:
            if "No Action" not in line:
                line = str(line)
                self.resultsFile.write(line + "\n")
                gu.log(line.replace("\n", ""))
                if self.settings["performanceTest"] == "True":
                    totalRecs += 1
                    if "INCORRECT" in line:
                        incorrectRecs += 1

        if self.settings["performanceTest"] == "True":
            string = (str(totalRecs-incorrectRecs) + " of " + str(totalRecs) + " correct")
            self.resultsFile.write(string)
            gu.log(string)

        self.resultsFile.close()

        allResults = "Results: \n"
        row_format = "{:>10} {:>20} {:>30} {:>10}"
        for result in self.results:
            allResults += (row_format.format("", *result) + "\n")
        gu.log(allResults)



    def start_worker(self, lock):
        #technicalIndicators = ["MACD", "BBANDS", "dayChange", "RSI", "CCI", "volumeROCP", "chaikinAD", "nasdaqChange", "ADMI", "stochastic", "aroon"]
        technicalIndicators = ["MACD", "BBANDS", "dayChange", "RSI", "CCI", "volumeROCP", "chaikinAD", "nasdaqChange", "ADMI", "stochastic", "aroon"]

        while True:
            lock.acquire()
            if len(self.stocks) > 0:
                myStock = self.stocks.pop(0)
                lock.release()
                x = (LineageClass.Lineage(myStock,
                                          technicalIndicators,
                                          self.settings))

                x.master_initialize()
                recommendation = x.evolve()
                giroScore = abs(recommendation[1][0] - recommendation[1][1]) #buy - sell
                self.results.append([myStock, recommendation[0], round(giroScore, 3)])

            else:
                lock.release()
                break