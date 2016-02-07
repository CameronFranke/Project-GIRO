__author__ = 'Cameron'
import GiroUtilities as gu
import InvestmentStrategyClass
from random import randrange
import numpy as np
import talib as tl

'''
        Yahoo finance does not provide access to data past a certain date.
TODO:
        -Need to refactor yahoo finance function so that it names the file according to the dates that
            are actually available as they may differ from the requested data and will not update if
            the dates listed are incorrect.

        - kpoint crossover

        -

'''

class Lineage():

    def __init__(self,
                 stockSymbol,
                 technicalIndicators,
                 settings):

        self.lookback = int(settings["lookbackLevel"])
        self.perfTest = settings["performanceTest"]
        self.settings = settings
        self.dateRange = {}
        self.indicatorsBeingUsed = []
        self.symbol = stockSymbol
        self.open = []
        self.high = []
        self.low = []
        self.close = []
        self.volume = []
        self.technicalIndicators = technicalIndicators
        self.populationSize = int(settings["populationSize"])
        self.population = []
        self.indicatorRange = {}
        self.generationCount = int(settings["generations"])
        self.data = []
        self.triggerThreshold = float(settings["triggerThreshold"])
        self.dayTriggerThreshold = float(settings["dayTriggerThreshold"])
        self.bestStrategyIndex = 0
        self.fitnessScores = []
        self.selectionPercentage = float(settings["selectionPercentage"])
        self.mutationRate = float(settings["mutationRate"])
        self.mutationRateDelta = float(settings["mutationRateDelta"])
        self.startingMoney = float(settings["startingMoney"])
        self.transactionCost = float(settings["transactionCost"])
        self.dayTrigIncrementGens = settings["incrementDayThresholdGens"]
        self.trigIncrementGens = settings["incrementTriggerThresholdGens"]
        self.dayTrigIncrementAmount = float(settings["dayTrigIncrementAmount"])
        self.trigIncrementAmount = float(settings["TrigIncrementAmount"])
        self.settings["tradeOnLossPunishment"] = float(settings["tradeOnLossPunishment"])
        self.lastDay = ""
        self.tournamentSize = int(settings["tournamentSize"])
        self.tradeLimit = int(self.settings["tradeCountLimit"])
        self.debug = True


    def evolve(self):
        gu.log("Beginning " + str(self.generationCount) + " generation simulation of " + self.symbol)
        for generations in range(self.generationCount):
            self.compute_fitness_scores()
            actions = 0
            for strategy in self.population:
                actions += strategy.actionCount
            actions /=self.populationSize
            gu.log(self.symbol + " Generation: " + str(generations) +
                   "\n\t\t\t\t\t\t\t\t\tHighest profit this round: " + str(round(max(self.fitnessScores), 2)) + "\t\t" + str(round((max(self.fitnessScores))/self.startingMoney*100, 2)) + "%" +
                   "\n\t\t\t\t\t\t\t\t\tAverage profit this round: " + str(round(np.average(self.fitnessScores), 2)) + "\t\t" + str(round((np.average(self.fitnessScores))/self.startingMoney*100, 2)) + "%" +
                   "\n\t\t\t\t\t\t\t\t\tMutation Rate: " + str(self.mutationRate) +
                   "\n\t\t\t\t\t\t\t\t\tAverage trade count: " + str(actions) +
                   "\n\t\t\t\t\t\t\t\t\tBest strategie's trade correctness: \t" + str(round(self.population[self.bestStrategyIndex].relativeCorrectness, 2)*100) + "%" +
                   "\n\t\t\t\t\t\t\t\t\tBest strategie's trade count: " + str(self.population[self.bestStrategyIndex].actionCount))
            self.tournament_selection()
            self.uniform_crossover()
            self.mutate_population()
            self.update_mutation_rate()

            if generations in self.dayTrigIncrementGens:
                self.dayTriggerThreshold += self.dayTrigIncrementAmount

            if generations in self.trigIncrementGens:
                self.triggerThreshold += self.trigIncrementAmount

        recommendation = self.population[self.bestStrategyIndex].finalTrade

        if recommendation == "NULL":
            recommendation = "No Action"
        else:
            if self.perfTest:
                if recommendation == "BUY/COVER":
                    if self.lastDay["close"] > self.data.pop()["close"]:
                        recommendation += "--CORRECT"
                    else:
                        recommendation += "--INCORRECT"

                elif recommendation == "SELL/SHORT":
                    if self.lastDay["close"] < self.data.pop()["close"]:
                        recommendation += "--CORRECT"
                    else:
                        recommendation += "--INCORRECT"


        gu.log(self.symbol + " action recommendation: " + recommendation)
        #self.population[self.bestStrategyIndex].print_constraints()

        self.data = ""
        self.population = ""        # manage hardware related memory issue on laptop?

        return recommendation


    def master_initialize(self):
        self.dateRange["startY"] = self.settings["startYear"]
        self.dateRange["startM"] = self.settings["startMonth"]
        self.dateRange["startD"] = self.settings["startDay"]
        self.dateRange["stopY"] = self.settings["stopYear"]
        self.dateRange["stopM"] = self.settings["stopMonth"]
        self.dateRange["stopD"] = self.settings["stopDay"]
        if self.perfTest == "True":
            self.perfTest = True
        else: self.perfTest = False

        self.data = gu.pull_Yahoo_Finance_Data(self.symbol, self.dateRange)
        if self.perfTest:
            self.lastDay = self.data.pop()

        self.parse_trigger_settings()
        self.compute_technical_indicators()
        self.compute_indicator_ranges()
        self.initialize_population()


    def print_Raw_Data(self):
        for dataPoint in self.data:
            tempString = ""
            for key in dataPoint:
                if key != "date":
                    tempString += key + ": " + str(np.round(dataPoint[key], 2)) + "\t\t"
                else:
                    tempString += key + ": " + str(dataPoint[key]) + "\t\t"


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


    def parse_trigger_settings(self):
        temp = []
        for x in self.dayTrigIncrementGens.split(","):
            temp.append(int(x))
        self.dayTrigIncrementGens = temp

        temp = []
        for x in self.trigIncrementGens.split(","):
            temp.append(int(x))
        self.trigIncrementGens = temp


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
                                                                              self.transactionCost,
                                                                              self.settings["tradeOnLossPunishment"],
                                                                              self.tradeLimit))


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


    def update_mutation_rate(self):
        if self.mutationRate > 0.00001:
            self.mutationRate += self.mutationRateDelta


    def compute_fitness_scores(self):
        bestStrategyIndex = 0
        scores = []

        for strategy in range(self.populationSize):
            self.population[strategy].compute_fitness_score_2()
            bestFitnessScore = self.population[bestStrategyIndex].fitnessScore
            scores.append(self.population[strategy].fitnessScore)

            if self.population[strategy].fitnessScore > bestFitnessScore:
                bestStrategyIndex = strategy

        self.bestStrategyIndex = bestStrategyIndex
        self.fitnessScores = scores


    def tournament_selection(self):

        newPopulation = []
        newPopulationSize = int(np.round((self.selectionPercentage * self.populationSize),0))   # need cast to in, python complains about the numpy type float32

        for i in range(newPopulationSize):
            contestants = []
            for competitor in range(self.tournamentSize):
                contestants.append(randrange(0, self.populationSize))

            contestantScores = []
            for contestant in contestants:
                contestantScores.append(self.fitnessScores[contestant])

            newPopulation.append(self.population[contestants[contestantScores.index(max(contestantScores))]])


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
                                                                              self.transactionCost,
                                                                              self.settings["tradeOnLossPunishment"],
                                                                              self.tradeLimit))


    def compute_technical_indicators(self):
        self.build_raw_price_list()
        for indicator in self.technicalIndicators:
            command = "self.compute_" + indicator + "()"
            exec(command)
        gu.log(self.symbol + " Technical indicator calculations complete")


    def compute_dayChange(self):
        self.indicatorsBeingUsed.append("dayChange")
        dayChangePercentage = [np.nan]
        for day in range(1,len(self.data)):
            dayChangePercentage.append(1-(self.data[day-1]["close"]/self.data[day]["close"]))
        self.update_data(dayChangePercentage, "dayChange")


    def update_data(self, indicatorResults, keyName):
        for dataPoint in range(len(self.data)):
            self.data[dataPoint][keyName] = indicatorResults[dataPoint]


    def build_raw_price_list(self):
        # this function should be renames
        for dataPoint in self.data:
            self.open.append(dataPoint["open"])
            self.high.append(dataPoint["high"])
            self.low.append(dataPoint["low"])
            self.close.append(dataPoint["close"])
            self.volume.append(dataPoint["volume"])

        self.open = np.array(self.open)
        self.high = np.array(self.high)
        self.low = np.array(self.low)
        self.close = np.array(self.close)
        self.volume = np.array(self.volume)


    def compute_SMA(self):
        SMA = tl.SMA(self.close)
        self.update_data(SMA, "SMA")
        self.indicatorsBeingUsed.append("SMA")


    def compute_MACD(self):
        MACD, MACDsignal, MACDdiff = tl.MACD(self.close, fastperiod=12, slowperiod=26, signalperiod=9)
        self.update_data(MACD, "MACD")
        self.update_data(MACDsignal, "MACDsignal")
        self.update_data(MACDdiff, "MACDdiff")
        self.indicatorsBeingUsed.append("MACD")
        self.indicatorsBeingUsed.append("MACDsignal")
        self.indicatorsBeingUsed.append("MACDdiff")


    def compute_BBANDS(self):
        upper, middle, lower = tl.BBANDS(self.close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        self.update_data(upper, "BBANDupper")
        self.update_data(middle, "BBANDmiddle")
        self.update_data(lower, "BBANDlower")
        self.indicatorsBeingUsed.append("BBANDupper")
        self.indicatorsBeingUsed.append("BBANDmiddle")
        self.indicatorsBeingUsed.append("BBANDlower")


    def compute_RSI(self):
        rsi = tl.RSI(self.close)
        self.update_data(rsi, "RSI")
        self.indicatorsBeingUsed.append("RSI")


    def compute_CCI(self):
        cci = tl.CCI(self.high, self.low, self.close)
        self.update_data(cci, "CCI")
        self.indicatorsBeingUsed.append("CCI")


    def compute_volumeROCP(self):
        #rate of change percentage
        volumeROCP = tl.ROCP(self.close)
        self.update_data(volumeROCP, "volumeROCP")
        self.indicatorsBeingUsed.append("volumeROCP")


    def compute_chaikinAD(self):
        chaikinAD = tl.ADOSC(self.high, self.low, self.close, self.volume)
        self.update_data(chaikinAD, "chaikinAD")
        self.indicatorsBeingUsed.append("chaikinAD")


    def compute_hammer(self):
        #hammer pattern
        hammer = tl.CDLHAMMER(self.open, self.high, self.low, self.close)
        self.update_data(hammer, "hammer")
        self.indicatorsBeingUsed.append("hammer")


    def compute_3starsSouth(self):
        #SEEMS TO BE BROKEN, ALWAYS RETURNS 0s
        #three stars in the south pattern
        startsSouth = tl.CDL3STARSINSOUTH(self.open, self.high, self.low, self.close)
        self.update_data(startsSouth, "3starsSouth")
        self.indicatorsBeingUsed.append("3starsSouth")


    def compute_3advancingSoldiers(self):
        #SEEMS TO BE BROKEN, ALWAYS RETURNS 0s
        #three advancing white soldiers pattern
        soldiers = tl.CDL3WHITESOLDIERS(self.open, self.high, self.low, self.close)
        self.update_data(soldiers, "3advancingSoldiers")
        self.indicatorsBeingUsed.append("3advancingSoldiers")


    def compute_morningStar(self):
        #morning star pattern
        star = tl.CDLMORNINGSTAR(self.open, self.high, self.low, self.close)
        self.update_data(star, "morningStar")
        self.indicatorsBeingUsed.append("morningStar")


    def compute_shootingStar(self):
        #shooting star pattern
        star = tl.CDLSHOOTINGSTAR(self.open, self.high, self.low, self.close)
        self.update_data(star, "shootingStar")
        self.indicatorsBeingUsed.append("shootingStar")


    def compute_nasdaqChange(self):
        nasdaq = gu.pull_Yahoo_Finance_Data("^IXIC", self.dateRange)
        temp = []
        for x in nasdaq:
            temp.append(np.double(x["close"]))
        nasdaq = np.array(temp)
        nasdaq = tl.ROCP(nasdaq)
        self.update_data(nasdaq, "nasdaqChange")
        self.indicatorsBeingUsed.append("nasdaqChange")


    def compute_ADMI(self):
        # average directional movement index rating
        ADMI = tl.ADXR(self.high, self.low, self.close)
        self.update_data(ADMI, "ADMI")
        self.indicatorsBeingUsed.append("ADMI")


    def compute_stochastic(self):
        slowk, slowd = tl.STOCH(self.high, self.low, self.close)
        self.update_data(slowk, "slowk")
        self.update_data(slowd, "slowd")
        self.indicatorsBeingUsed.append("slowk")
        self.indicatorsBeingUsed.append("slowd")


    def compute_OBV(self):
        # on balance volume indicator
        # DOES NOT APPEAR TO BE WORKING PROPERLY
        obv = np.array
        obv = tl.OBV(self.volume)
        print obv
        self.update_data(obv, "OBV")
        self.indicatorsBeingUsed.append("OBV")


    def compute_aroon(self):
        aroonDown, aroonUp = tl.AROON(self.high, self.low)
        self.update_data(aroonDown, "aroonDown")
        self.update_data(aroonUp, "aroonUp")
        self.indicatorsBeingUsed.append("aroonDown")
        self.indicatorsBeingUsed.append("aroonUp")