__author__ = 'Cameron'
import GiroUtilities as gu
import InvestmentStrategyClass
from random import randrange
import numpy as np
import talib as tl
import urllib2

'''
        Yahoo finance does not provide access to data past a certain date.
TODO:
        Need to refactor yahoo finance function so that it names the file according to the dates that
            are actually available as they may differ from the requested data and will not update if
            the dates listed are incorrect.

        TECHNICAL INDICATORS TO ADD:
            - RSI
            - volatility
            - NASQAQ/DOW EMA, RSI
            - pattern recognition....
'''

class Lineage():

    def __init__(self,
                 stockSymbol,
                 dateRange,
                 technicalIndicators,
                 populationSize,
                 generationCount,
                 lookbackLevel,
                 triggerThreshold,
                 dayTriggerThreshold,
                 selectionPercentage,
                 mutationRate,
                 mutationRateDelta,
                 startingMoney,
                 transactionCost):

        self.lookback = lookbackLevel
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
        self.triggerThreshold = triggerThreshold
        self.dayTriggerThreshold = dayTriggerThreshold
        self.bestStrategyIndex = 0
        self.fitnessScores = []
        self.selectionPercentage = selectionPercentage
        self.mutationRate = mutationRate
        self.mutationRateDelta = mutationRateDelta
        self.startingMoney = startingMoney
        self.transactionCost = transactionCost
        self.debug = True


    def evolve(self):
        gu.log("Beginning " + str(self.generationCount) + " generation simulation of " + self.symbol)
        for generations in range(self.generationCount):
            self.compute_fitness_scores()
            gu.log(self.symbol + " Generation: " + str(generations) +
                   "\n\t\t\t\t\t\t\t\t\tHighest fitness this round: " + str(max(self.fitnessScores)) +
                   "\n\t\t\t\t\t\t\t\t\tAverage fitness this round: " + str(np.average(self.fitnessScores)))
            self.tournament_selection()
            self.uniform_crossover()
            self.mutate_population()
            self.updata_mutation_rate()

        recommendation = self.population[self.bestStrategyIndex].finalTrade

        if recommendation == "NULL":
            recommendation = "No Action"

        gu.log(self.symbol + " action recommendation: " + recommendation)
        return recommendation


    def master_initialize(self):
        self.pull_Yahoo_Finance_Data()
        self.compute_technical_indicators()
        self.compute_indicator_ranges()
        self.initialize_population()


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

            gu.log("Download URL: " + base)

            response = urllib2.urlopen(base)
            response = str(response.read())
            response = response.splitlines()
            response.pop(0)

            for line in response:
                line = line.split(",")
                temp= {}
                temp["date"] = line[0]
                temp["price"] = np.double(line[6])
                self.data.append(temp)
            self.data.reverse()

            gu.log("Creating storage file for " + self.symbol)
            nf = open(fileName, 'w+')
            for dataPoint in self.data:
                nf.write(dataPoint["date"] + " " + str(dataPoint["price"]) + "\n")
            nf.close()


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
        for i in range(self.populationSize):    # number of strategies to make
            myStrategies = []
            for x in range(self.lookback):      # number of period lookbacks
                myTriggers = {}
                for indicator in self.indicatorsBeingUsed:  # for each indicator
                    test = np.random.uniform(initializationRanges[indicator][0], initializationRanges[indicator][1], 4)
                    test1 = []
                    for i in test:
                        test1.append(np.round(i,3))
                    test = test1

                    temp = {}
                    temp["BuyLower"] = test[0]
                    temp["BuyUpper"] = test[1]
                    temp["SellLower"] = test[2]
                    temp["SellUpper"] = test[3]

                    myTriggers[indicator] = temp
                myStrategies.append(myTriggers)

            self.population.append(InvestmentStrategyClass.InvestmentStrategy(myStrategies,
                                                                              self.data,
                                                                              self.lookback,
                                                                              self.triggerThreshold,
                                                                              self.dayTriggerThreshold,
                                                                              self.indicatorsBeingUsed,
                                                                              self.startingMoney,
                                                                              self.transactionCost))

        gu.log("Population initialiazed with " + str(self.populationSize) + " investment strategies")


    def mutate_population(self):
        for strategy in range(len(self.population)):
            for day in range(len(self.population[strategy].constraints)):
                for indicator in self.population[strategy].constraints[day]:
                    for boundingValue in self.population[strategy].constraints[day][indicator]:
                        chance = float(randrange(0, 100000))
                        if chance <= (self.mutationRate * 100000):
                            mutationMultiplier = float(randrange(-100, 100))
                            mutationMultiplier = 1 + (mutationMultiplier / 100)
                            newValue = self.population[strategy].constraints[day][indicator][boundingValue] * mutationMultiplier
                            self.population[strategy].constraints[day][indicator][boundingValue] = newValue


    def updata_mutation_rate(self):
        if self.mutationRate > 0:
            self.mutationRate += self.mutationRateDelta


    def compute_fitness_scores(self):
        bestStrategyIndex = 0
        scores = []

        for strategy in range(self.populationSize):
            self.population[strategy].compute_fitness_score()
            bestFitnessScore = self.population[bestStrategyIndex].fitnessScore
            scores.append(self.population[strategy].fitnessScore)

            if self.population[strategy].fitnessScore > bestFitnessScore:
                bestStrategyIndex = strategy

        self.bestStrategyIndex = bestStrategyIndex
        self.fitnessScores = scores


    def roulette_wheel_selection(self):
        print("Placeholder- Function not implemented")
        '''
        This might be the best method to use but it is slightly more computationally intensive and
        time consuming to write so I will use tournament selection until I can talk to Dr. Hayes

        CONST_BASE_DIVISOR = 2

        strategiesToSelect = np.round((self.populationSize*self.selectionPercentage), 0)
        temp = []
        for i in self.fitnessScores:
            if i > 0:
                temp.append(i)

        baseChance = min(temp)/CONST_BASE_DIVISOR
        chancePoints = []
        newPopulation = []

        for i in self.fitnessScores:
            if i < 0:
                chancePoints.append(baseChance)
            else:
                chancePoints.append(baseChance + i)

        totalPoints = sum(chancePoints)
        temp = list(chancePoints)
        for i in range(len(temp)):
            chancePoints =

        for i in range(strategiesToSelect):
            print
        '''
        print("Placeholder- Function not implemented")


    def tournament_selection(self):

        newPopulation = []
        newPopulationSize = int(np.round((self.selectionPercentage * self.populationSize),0))   # need cast to in, python complains about the numpy type float32

        for i in range(newPopulationSize):
            indexX = randrange(0, self.populationSize)
            indexY = randrange(0, self.populationSize)
            x = self.fitnessScores[indexX]
            y = self.fitnessScores[indexY]

            if x > y:
                newPopulation.append(self.population[indexX])
            else:
                newPopulation.append(self.population[indexY])

        self.population = newPopulation


    def uniform_crossover(self):

        triggerNames = ["BuyLower", "BuyUpper", "SellLower", "SellUpper"]

        crossoverPopulationSize = self.populationSize - len(self.population)
        selectedPopulationSize = len(self.population)

        for strategy in range(crossoverPopulationSize):
            #choose strategies to dual
            indexA = randrange(0, selectedPopulationSize)
            indexB = randrange(0, selectedPopulationSize)
            parents = [indexA, indexB]
            entireStratedy = []
            for day in range(self.lookback):
                dayStrategy = {}
                for indicator in self.indicatorsBeingUsed:
                    temp = {}
                    for trigger in triggerNames:
                        parent = randrange(0,2)
                        temp[trigger] = self.population[parents[parent]].constraints[day][indicator][trigger]

                    dayStrategy[indicator] = temp
                entireStratedy.append(dayStrategy)

            self.population.append(InvestmentStrategyClass.InvestmentStrategy(entireStratedy,
                                                                              self.data,
                                                                              self.lookback,
                                                                              self.triggerThreshold,
                                                                              self.dayTriggerThreshold,
                                                                              self.indicatorsBeingUsed,
                                                                              self.startingMoney,
                                                                              self.transactionCost))


    def compute_technical_indicators(self):
        self.build_raw_price_list()
        for indicator in self.technicalIndicators:
            command = "self.compute_" + indicator + "()"
            exec(command)
        gu.log("Technical indicator calculations complete")


    def compute_dayChange(self):
        self.indicatorsBeingUsed.append("dayChange")
        dayChangePercentage = [np.nan]
        for day in range(1,len(self.data)):
            dayChangePercentage.append(1-(self.data[day-1]["price"]/self.data[day]["price"]))
        self.update_data(dayChangePercentage, "dayChange")


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
        self.indicatorsBeingUsed.append("BBANDlower")