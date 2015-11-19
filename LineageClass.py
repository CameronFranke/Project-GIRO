__author__ = 'Cameron'
import GiroUtilities as gu
import numpy as np
import talib as tl
import urllib2

'''
TODO:
'''


class Lineage():

    def __init__(self, stockSymbol, dateRange, technicalIndicators, populationSize, generationCount):

        self.dateRange = dateRange
        self.indicatorsBeingUsed = []
        self.symbol = stockSymbol
        self.priceOnly = []
        self.technicalIndicators = technicalIndicators
        self.populationSize = populationSize
        self.population = []
        self.indicatorRange = {}
        self.generationCount = generationCount
        self.data = []
        self.debug = True


    def pull_Yahoo_Finance_Data(self):

        fileName = "StockData/"\
                   + self.symbol + ":"\
                   + self.dateRange["startM"]\
                   + "-" + self.dateRange["startD"]\
                   + "-" + self.dateRange["startY"]\
                   + "_" + self.dateRange["stopM"]\
                   + "-" + self.dateRange["stopD"]\
                   + "-" + self.dateRange["stopY"]\
                   + ".txt"

        gu.log(fileName)

        try:
            f = open(fileName, "r")
            data = f.readlines()
            tempData = []
            gu.log("Using stored data for " + self.symbol)
            for line in data:
                temp = line.rstrip()
                temp = temp.split(" ")
                tempDict = {}
                tempDict["date"] = temp[0]
                tempDict["price"] = np.double(temp[1])
                tempData.append(tempDict)
            f.close()
            self.data = tempData

        except:
            gu.log("No stored data available for " + self.symbol)
            gu.log("Pulling stock data for " + self.symbol + " from yahoo")

            base = "http://ichart.yahoo.com/table.csv?s="\
                   + self.symbol\
                   + "&a=" + self.dateRange["startM"]\
                   + "&b=" + self.dateRange["startD"]\
                   + "&c=" + self.dateRange["startY"]\
                   + "&d=" + self.dateRange["stopM"]\
                   + "&e=" + self.dateRange["stopD"]\
                   + "&f=" + self.dateRange["stopY"]\
                   + "&g=d&ignore=.cvs"

            response = urllib2.urlopen(base)
            response = str(response.read())
            response = response.splitlines()

            for line in response:
                line = line.split(",")
                temp= {}
                temp["date"] = line[0]
                temp["price"] = np.double(line[6])
                self.data.append(temp)
            self.data.pop(0)

            gu.log("Creating storage file for " + self.symbol)
            nf = open(fileName, 'w+')
            for dataPoint in self.data:
                nf.write(dataPoint["date"] + " " + str(dataPoint["price"]) + "\n")


    def print_Raw_Data(self):
        for dataPoint in self.data:
            tempString = ""
            for key in dataPoint:
                if key != "date":
                    tempString += key + ": " + str(np.round(dataPoint[key], 2)) + "\t\t"
                else:
                    tempString += key + ": " + str(dataPoint[key]) + "\t\t"
            print tempString


    def compute_indicator_ranges(self):
        for indicator in self.indicatorsBeingUsed:
            temp = []
            for dataPoint in self.data:
                if np.logical_not(np.isnan(dataPoint[indicator])):
                    temp.append(dataPoint[indicator])
            self.indicatorRange[(indicator + "min")] = min(temp)
            self.indicatorRange[(indicator + "max")] = max(temp)
            self.indicatorRange[(indicator + "range")] = max(temp) - min(temp)
            self.indicatorRange[(indicator + "average")] = np.average(temp)

    def initialize_population(self):
        # Create the actual range of values that will make up the strategy trigger values

        CONST_RANGE_MULTIPLIER = 1.15
        initializationRanges = {}
        for indicator in self.indicatorsBeingUsed:
            x = self.indicatorRange[(indicator + "average")] - self.indicatorRange[(indicator + "min")]
            initLowerBound = self.indicatorRange[(indicator + "average")] - (CONST_RANGE_MULTIPLIER * x)
            x = self.indicatorRange[(indicator + "max")] - self.indicatorRange[(indicator + "average")]
            initUpperBound = self.indicatorRange[(indicator + "average")] + (CONST_RANGE_MULTIPLIER * x)
            temp = []
            temp.append(initLowerBound)
            temp.append(initUpperBound)
            initializationRanges[indicator] = temp

        # initialize the population
        for i in range(self.populationSize):
            myTriggers = {}
            for i in self.indicatorsBeingUsed:
                x = np.random.random_integers(initializationRanges[i][0], initializationRanges[i][1])
                y = np.random.random_integers(initializationRanges[i][0], initializationRanges[i][1])
                if x < y:           # x should be the upper value
                    y, x = x, y
                myTriggers[i] = [x,y]

            print myTriggers




    def compute_technical_indicators(self):
        self.build_raw_price_list()
        for indicator in self.technicalIndicators:
            command = "self.compute_" + indicator + "()"
            exec(command)
        gu.log("Technical indicator calculations complete")


    def update_data(self, indicatorResults, keyName):
        for dataPoint in range(len(self.data)):
            self.data[dataPoint][keyName] = indicatorResults[dataPoint]


    def build_raw_price_list(self):

        for dataPoint in self.data:
            self.priceOnly.append(dataPoint["price"])
        self.priceOnly = np.array(self.priceOnly)


    def compute_SMA(self):
        SMA = tl.SMA(self.priceOnly)
        self.update_data(SMA, "SMA")
        self.indicatorsBeingUsed.append("SMA")


    def compute_MACD(self):
        MACD, MACDsignal, MACDdiff = tl.MACD(self.priceOnly, fastperiod=12, slowperiod=26, signalperiod=9)
        self.update_data(MACD, "MACD")
        self.update_data(MACDsignal, "MACDsignal")
        self.update_data(MACDdiff, "MACDdiff")
        self.indicatorsBeingUsed.append("MACD")
        self.indicatorsBeingUsed.append("MACDsignal")
        self.indicatorsBeingUsed.append("MACDdiff")


    def compute_BBANDS(self):
        upper, middle, lower = tl.BBANDS(self.priceOnly, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        self.update_data(upper, "BBANDupper")
        self.update_data(middle, "BBANDmiddle")
        self.update_data(lower, "BBANDlower")
        self.indicatorsBeingUsed.append("BBANDupper")
        self.indicatorsBeingUsed.append("BBANDmiddle")
        self.indicatorsBeingUsed.append("BBANDupper")