__author__ = 'Cameron'
import GiroUtilities as gu

class InvestmentStrategyClass():

    def __init__(self, triggerConstraints, historicalData):

        self.triggerConstraints = triggerConstraints
        self.historicalData = historicalData
        self.fitnessScore = -10000.00
        self.profit = 0
        self.tradeCount = 0
        self.Debug = True

