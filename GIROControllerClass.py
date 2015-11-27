__author__ = 'Cameron'
import LineageClass
import GiroUtilities as gu

class GiroController():

    def __init__(self, resultsFile, stocksFile):
        self.results = open(resultsFile, "w+")
        self.stocks = stocksFile

    def init_stock_list(self):
        f = open(self.stocks, "r")
        f = f.readlines()
        temp = []
        for line in f:
            symbol = line.rstrip()
            temp.append(symbol)

        self.stocks = temp
        print self.stocks

    def giro_start(self):

        technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange"]

        dateRange = {}
        dateRange["startM"] = "00"
        dateRange["startD"] = "01"
        dateRange["startY"] = "2015"
        dateRange["stopM"] = "11"
        dateRange["stopD"] = "31"
        dateRange["stopY"] = "2015"

        triggerThreshold = .30
        dayTriggerThreshold = .50

        lookbackLevel = 3

        generations = 3
        populationSize = 8

        selectionPercentage = .75

        for stock in self.stocks:
            x = LineageClass.Lineage(stock,
                                    dateRange,
                                    technicalIndicators,
                                    populationSize,
                                    generations,
                                    lookbackLevel,
                                    triggerThreshold,
                                    dayTriggerThreshold,
                                    selectionPercentage)
            x.master_initialize()
            recommendation = x.evolve()
            gu.log("Recommendation: " + recommendation)