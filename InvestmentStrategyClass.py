__author__ = 'Cameron'
import GiroUtilities as gu
import numpy as np

'''
    TODO:
        - find numpy tools to clean up fitness function <-- it is messy and inefficient
        - mode where system can record the dates of trades and write them to a file
        - weight days
        - judge correct/incorrect strategies based on price action for a few days following recommendation
'''

class InvestmentStrategy():

    def __init__(self, triggerConstraints, historicalData, lookbackLevel, triggerThreshold, lookbackthreshold, indicatorsUsed, startingMoney, transactionCost, punishment, tradeLimit):

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
        self.punishment = punishment
        self.badTrades = 0
        self.Debug = False
        self.actionCount = 0
        self.relativeCorrectness = 0
        self.tradeLimit = tradeLimit
        self.buysellScores = [0,0]
        #print lookbackthreshold = daytriggerthreshold
        #print triggerThreshold = triggerthreshold


    def print_constraints(self):
        for day in range(self.lookback):
            print("Day-" + str(day))
            for indicator in self.constraints[day]:
                print ("\t" + indicator)
                for constraint in self.constraints[day][indicator]:
                    print("\t\t" + constraint + ": " + str(self.constraints[day][indicator][constraint]))

    def save_constraint_set(self, savefileName):
        savefile = open("Strategies/" + savefileName, "w+")
        savefile.write(str(self.constraints))

    def compute_fitness_score(self):
        self.actionCount = 0
        self.badTrades = 0
        trades = 0
        myCash = self.startingCash
        invested = 0
        valueOnLastAction = self.startingCash
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
                    lookbackTriggers[lookbackIndex] = 'b'

                elif sellSignals > buySignals and sellSignals > self.triggerThreshold:  # if sell trigger
                    lookbackTriggers[lookbackIndex] = 's'

            # count up lookback signals
            if (lookbackTriggers.count('b') - lookbackTriggers.count('s')) > self.lookbackThreshold:
                self.actionCount += 1
                if myCash != 0:
                    invested = myCash - self.transactionCost
                    if invested < valueOnLastAction:
                        invested = invested * (1-self.punishment)
                        self.badTrades += 1
                    myCash = 0
                    trades += 1
                    lastTrade = "BUY/COVER"
                    valueOnLastAction = invested
                else:
                    lastTrade = "BUY/COVER"

            elif (lookbackTriggers.count('s') - lookbackTriggers.count('b')) > self.lookbackThreshold:
                self.actionCount += 1
                if invested != 0:
                    myCash = invested - self.transactionCost
                    if myCash < valueOnLastAction:
                        myCash = myCash * (1-self.punishment)
                        self.badTrades += 1
                    invested = 0
                    trades += 1
                    lastTrade = "SELL/SHORT"
                    valueOnLastAction = myCash
                else:
                    lastTrade = "SELL/SHORT"

            if self.actionCount >= self.tradeLimit:
                break

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
            self.fitnessScore = profit

        if lastTrade != "":
            self.finalTrade = lastTrade

        if self.actionCount > 0:
            self.relativeCorrectness = 1 - (float(self.badTrades)/float(self.actionCount))


    def compute_fitness_score_2(self):
        self.actionCount = 0
        self.badTrades = 0
        trades = 0
        myCash = self.startingCash
        invested = 0
        valueOnLastAction = self.startingCash

        for dayIndex in range(self.lookback, len(self.historicalData)):
            lastTrade = "NULL"
            invested = invested * (1 + self.historicalData[dayIndex]["dayChange"])      # update value of investments
            triggers = []

            dayBuyStrength = 0
            daySellStrength = 0
            for indicator in self.constraints[0]:
                value = self.historicalData[dayIndex][indicator]
                contstraintBuyTriggers = 0
                contstraintSellTriggers = 0
                for day in range(self.lookback):
                    if self.constraints[day][indicator]["BuyUpper"] > value > self.constraints[day][indicator]["BuyLower"]:
                        contstraintBuyTriggers += 1
                    if self.constraints[day][indicator]["SellUpper"] > value > self.constraints[day][indicator]["SellLower"]:
                        contstraintSellTriggers += 1
                if contstraintBuyTriggers - contstraintSellTriggers >= self.lookbackThreshold:
                    dayBuyStrength += (1 * self.constraints[day][indicator]["BuyWeight"])
                elif contstraintSellTriggers - contstraintBuyTriggers >= self.lookbackThreshold:
                    daySellStrength += (1 * self.constraints[day][indicator]["SellWeight"])

            self.buysellScores = [dayBuyStrength, daySellStrength]
            # count up lookback signals
            if (dayBuyStrength - daySellStrength) >= self.triggerThreshold:
                self.actionCount += 1
                if myCash != 0:
                    invested = myCash - self.transactionCost
                    if invested < valueOnLastAction:
                        invested = invested * (1-self.punishment)
                        self.badTrades += 1
                    myCash = 0
                    trades += 1
                    lastTrade = "BUY/COVER"
                    valueOnLastAction = invested
                else:
                    lastTrade = "BUY/COVER"

            elif (daySellStrength - dayBuyStrength) >= self.triggerThreshold:
                self.actionCount += 1
                if invested != 0:
                    myCash = invested - self.transactionCost
                    if myCash < valueOnLastAction:
                        myCash = myCash * (1-self.punishment)
                        self.badTrades += 1
                    invested = 0
                    trades += 1
                    lastTrade = "SELL/SHORT"
                    valueOnLastAction = myCash
                else:
                    lastTrade = "SELL/SHORT"

            if self.actionCount >= self.tradeLimit:
                break

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
            self.fitnessScore = profit

        if lastTrade != "":
            self.finalTrade = lastTrade

        if self.actionCount > 0:
            self.relativeCorrectness = 1 - (float(self.badTrades)/float(self.actionCount))