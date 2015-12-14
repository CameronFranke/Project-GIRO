__author__ = 'Cameron'
import LineageClass
import GiroUtilities as gu
import threading
global stockThreads
'''
TODO:
'''

class GiroController():

    def __init__(self, resultsFile, stocksFile, configFile):
        self.configFile = configFile
        self.results = open(resultsFile, "w+")
        self.stocks = stocksFile
        self.settings = {}
        self.resultsLock = threading.Lock()

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


    def giro_start(self):
        global stockThreads
        technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange"]

        dateRange = {}
        dateRange["startM"] = "00"
        dateRange["startD"] = "01"
        dateRange["startY"] = "2015"
        dateRange["stopM"] = "11"
        dateRange["stopD"] = "31"
        dateRange["stopY"] = "2015"

        stockThreads = []
        for stock in self.stocks:
            x = (LineageClass.Lineage(stock,
                                                    dateRange,
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
            y = threading.Thread(target=self.start_thread, args=(x,))
            stockThreads.append(y)

        for x in stockThreads:
            x.start()

        for x in stockThreads:
            x.join()

        self.results.close()


    def start_thread(self, stock):
        stock.master_initialize()
        recommendation = stock.evolve()
        self.resultsLock.acquire()
        self.results.write(str(stock.symbol) + ": " + recommendation + "\n")
        self.resultsLock.release()
