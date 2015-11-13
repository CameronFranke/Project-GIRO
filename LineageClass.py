__author__ = 'Cameron'
import GiroUtilities as gu
import talib
import yahoo_finance as yf
import urllib2

class Lineage():

    def __init__(self, stockSymbol, populationSize, generationCount):

        self.symbol = stockSymbol
        self.populationSize = populationSize
        self.population = []
        self.generationCount = generationCount
        self.data = []

    def pullYahooFinanceData(self):
        '''
        startDate = "2013-01-01"
        endDate = "2014-12-30"
        yahoo = yf.Share(self.symbol)
        print yahoo.get_historical()
        '''

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
            temp["price"] = line[6]
            self.data.append(temp)