__author__ = 'Cameron'
import GiroUtilities as gu
import numpy as np
import talib as tl
import urllib2

'''
TODO:
    - clean up raw data output so that the lines line up
'''


class Lineage():

    def __init__(self, stockSymbol, dateRange, technicalIndicators, populationSize, generationCount):

        self.dateRange = dateRange
        self.symbol = stockSymbol
        self.priceOnly = []
        self.technicalIndicators = technicalIndicators
        self.populationSize = populationSize
        self.population = []
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
                tempString += key + ": " + str(dataPoint[key]) + "\t\t"
            print tempString


    def compute_technical_indicators(self):
        self.build_raw_price_list()
        for indicator in self.technicalIndicators:
            command = "self.compute_" + indicator + "()"
            exec(command)
        gu.log("Technical indicator calculations complete")


    def compute_SMA(self):
        SMA = tl.SMA(self.priceOnly)
        self.update_data(SMA, "SMA")


    def update_data(self, indicatorResults, keyName):
        for dataPoint in range(len(self.data)):
            self.data[dataPoint][keyName] = indicatorResults[dataPoint]


    def build_raw_price_list(self):

        for dataPoint in self.data:
            self.priceOnly.append(dataPoint["price"])
        self.priceOnly = np.array(self.priceOnly)