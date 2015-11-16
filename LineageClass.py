__author__ = 'Cameron'
import GiroUtilities as gu
import talib
import urllib2

class Lineage():

    def __init__(self, stockSymbol, populationSize, generationCount):

        self.symbol = stockSymbol
        self.populationSize = populationSize
        self.population = []
        self.generationCount = generationCount
        self.data = []

    def pullYahooFinanceData(self):

        base = "http://ichart.yahoo.com/table.csv?s="
        base += self.symbol + "&a=1&b=1&c=2010"         #start date: month, day, year
        base += "&d=12&e=31&f=2014"                     #ending data: month, day, year
        base += "&g=d"                                  #interval
        base += "&ignore=.cvs"                          #data format

        response = urllib2.urlopen(base)
        response = str(response.read())
        response = response.splitlines()

        for line in response:
            line = line.split(",")
            temp= {}
            temp["date"] = line[0]
            temp["price"] = line[6]             # convert to numpy types
            self.data.append(temp)

            #should precompute a file name, and dump data to file
            #if data is present in the file with the same start and end data then use
            #data from file instead of making the api call


    def computeAtechnicalIndicator(self):
        # use TAlib to copute the technical indicators
        # 1 function per indicator