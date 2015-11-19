__author__ = 'Cameron'
import GiroUtilities as gu

class InvestmentStrategy():

    def __init__(self, triggerConstraints, historicalData, lookbackLevel):

        self.lookback = lookbackLevel
        self.constraints = triggerConstraints
        self.historicalData = historicalData
        self.fitnessScore = -10000.00
        self.profit = 0
        self.tradeCount = 0
        self.Debug = True

    def print_constraints(self):
        for day in range(self.lookback):
            print("Day-" + str(day) + ": " + str(self.constraints[day]))

