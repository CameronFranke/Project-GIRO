__author__ = 'Cameron'
import GiroUtilities as gu

'''
    TODO:
        - actually write the damn fitness function
'''

class InvestmentStrategy():

    def __init__(self, triggerConstraints, historicalData, lookbackLevel, triggerThreshold, lookbackthreshold):

        self.lookback = lookbackLevel
        self.constraints = triggerConstraints
        self.historicalData = historicalData
        self.fitnessScore = -10000.00
        self.triggerThreshold = triggerThreshold
        self.lookbackThreshold = lookbackthreshold
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
        for x in self.historicalData:
            print x

