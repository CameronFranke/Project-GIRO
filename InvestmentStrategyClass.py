__author__ = 'Cameron'
import GiroUtilities as gu
import numpy as np

'''
    TODO:
        - prepare to implement mutation function
        - find numpy exponent function to clean up fitness function
        - fitness score needs to be adjusted... static multiplier maybe- also needs more precise type
        - need a mutation/immegration function
        - DOWJ and NASDAQ day change averages
'''

class InvestmentStrategy():

    def __init__(self, triggerConstraints, historicalData, lookbackLevel, triggerThreshold, lookbackthreshold, indicatorsUsed, startingMoney, transactionCost):

        self.indicatorsUsed = indicatorsUsed
        self.lookback = lookbackLevel
        self.constraints = triggerConstraints
        self.historicalData = historicalData
        self.fitnessScore = -1000000.00
        self.startingCash = startingMoney
        self.transactionCost = transactionCost
        self.triggerThreshold = int(triggerThreshold*len(self.constraints[0]))
        self.lookbackThreshold = int(lookbackthreshold*self.lookback)
        self.profit = 0
        self.tradeCount = 0
        self.finalTrade = "NULL"
        self.Debug = False


    def print_constraints(self):
        for day in range(self.lookback):
            print("Day-" + str(day))
            for indicator in self.constraints[day]:
                print ("\t" + indicator)
                for constraint in self.constraints[day][indicator]:
                    print("\t\t" + constraint + ": " + str(self.constraints[day][indicator][constraint]))


    def compute_fitness_score(self):
        trades = 0
        myCash = self.startingCash
        invested = 0
        for dayIndex in range(self.lookback, len(self.historicalData)):
            lastTrade = "NULL"
            invested = invested * (1 + self.historicalData[dayIndex]["dayChange"])      # update value of investments
            lookbackTriggers = [0]*self.lookback

            for lookbackIndex in range(self.lookback):
                buySignals = 0
                sellSignals = 0

                for indicator in self.indicatorsUsed:
                    value = self.historicalData[dayIndex][indicator]
                    if self.constraints[lookbackIndex][indicator]["BuyUpper"] > value > self.constraints[lookbackIndex][indicator]["BuyLower"]:
                        buySignals += 1
                    elif self.constraints[lookbackIndex][indicator]["SellUpper"] > value > self.constraints[lookbackIndex][indicator]["SellLower"]:
                        sellSignals += 1

                if buySignals > sellSignals and buySignals > self.triggerThreshold:    # if buy trigger
                    #if myCash != 0:
                    lookbackTriggers[lookbackIndex] = 'b'

                elif sellSignals > buySignals and sellSignals > self.triggerThreshold:  # if sell trigger
                    #if invested != 0:
                    lookbackTriggers[lookbackIndex] = 's'

            # count up lookback signals
            if lookbackTriggers.count('b') > self.lookbackThreshold and lookbackTriggers.count('b') > lookbackTriggers.count('s'):
                if myCash != 0:
                    invested = myCash - self.transactionCost
                    myCash = 0
                    trades += 1
                    lastTrade = "BUY/COVER"
                else:
                    lastTrade = "BUY/COVER"

            elif lookbackTriggers.count('s') > self.lookbackThreshold and lookbackTriggers.count('s') > lookbackTriggers.count('b'):
                if invested != 0:
                    myCash = invested - self.transactionCost
                    invested = 0
                    trades += 1
                    lastTrade = "SELL/SHORT"
                else:
                    lastTrade = "SELL/SHORT"

            if self.Debug:
                gu.log("Cash = " + str(myCash) + " \t Invested: " + str(invested))

        if invested != 0:
            profit = invested - self.startingCash
        else:
            profit = myCash - self.startingCash
        self.profit = profit
        if self.Debug:
            gu.log("Profit: " + str(profit))
            gu.log("Number of trades: " + str(trades))

        # aggregate fitness scoring
        if trades > 0:
            profitPerTrade = profit/float(trades)
        else:
            profitPerTrade = 0
        if self.Debug: gu.log("Average profit per trade: " + str(profitPerTrade))

        if trades > 0:
            # log function maybe...
            #testFitnessScore = np.round((profit*np.log10(np.abs(trades + 1))), 2)

            #if self.Debug: gu.log("Aggregate fitness score: " + str(testFitnessScore))

            #self.fitnessScore = testFitnessScore
            self.fitnessScore = profit

        if lastTrade != "":
            self.finalTrade = lastTrade