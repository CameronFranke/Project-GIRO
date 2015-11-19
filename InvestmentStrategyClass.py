__author__ = 'Cameron'
import GiroUtilities as gu

'''
    TODO:
        - factor in lookback
        - verify fitness function
        - prepate to implement mutation function
'''

class InvestmentStrategy():

    def __init__(self, triggerConstraints, historicalData, lookbackLevel, triggerThreshold, lookbackthreshold, indicatorsUsed):

        self.indicatorsUsed = indicatorsUsed
        self.lookback = lookbackLevel
        self.constraints = triggerConstraints
        self.historicalData = historicalData
        self.fitnessScore = -10000.00
        self.triggerThreshold = int(triggerThreshold*len(self.constraints[0]))
        self.lookbackThreshold = int(lookbackthreshold*self.lookback)
        self.profit = 0
        self.tradeCount = 0
        self.Debug = True

    def print_constraints(self):
        for day in range(self.lookback):
            print("Day-" + str(day))
            for indicator in self.constraints[day]:
                print ("\t" + indicator)
                for constraint in self.constraints[day][indicator]:
                    print("\t\t" + constraint + ": " + str(self.constraints[day][indicator][constraint]))

    def compute_fitness_score(self):
        cash = 100000
        invested = 0
        for dayIndex in range(self.lookback, len(self.historicalData)):
            invested = invested * (1 + self.historicalData[dayIndex]["dayChange"])      # update value of investments
            buySignals = 0
            sellSignals = 0
            for indicator in self.indicatorsUsed:
                value = self.historicalData[dayIndex][indicator]
                if self.constraints[0][indicator]["BuyUpper"] > value > self.constraints[0][indicator]["BuyLower"]:
                    buySignals += 1
                elif self.constraints[0][indicator]["SellUpper"] > value > self.constraints[0][indicator]["SellLower"]:
                    sellSignals += 1

            if buySignals > sellSignals and buySignals > self.triggerThreshold:    # if buy trigger
                if cash != 0:
                    invested = cash
                    cash = 0

            elif sellSignals > buySignals and sellSignals > self.triggerThreshold:  # if sell trigger
                if invested != 0:
                    cash = invested
                    invested = 0

            if self.Debug:
                gu.log("Cash = " + str(cash) + " \t Invested: " + str(invested))