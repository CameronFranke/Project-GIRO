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

    def __init__(self, triggerConstraints, historicalData, lookbackLevel, triggerThreshold, lookbackthreshold, indicatorsUsed, startingMoney, transactionCost, punishment, tradeLimit, shortRatio, marginInterest, stoploss):

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
        self.shortRatio = float(shortRatio)
        self.marginInterest = float(marginInterest)
        self.stoploss = stoploss


    def print_constraints(self):
        for day in range(self.lookback):
            print("Day-" + str(day))
            for indicator in self.constraints[day]:
                print ("\t" + indicator)
                for constraint in self.constraints[day][indicator]:
                    print("\t\t" + constraint + ": " + str(self.constraints[day][indicator][constraint]))


    def save_constraint_set(self, savefileName):
        savefile = open(savefileName, "a")
        savefile.write(str(self.constraints) + "\n")
        return self.constraints


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
            flag = False
            if (dayBuyStrength - daySellStrength) >= self.triggerThreshold:
                flag = True
                if myCash != 0:
                    self.actionCount += 1
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

            if flag == False and ((daySellStrength - dayBuyStrength) >= self.triggerThreshold):
                flag = True
                if invested != 0:
                    self.actionCount += 1
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

            if flag == False and invested != 0 and valueOnLastAction *(1-self.stoploss) > invested: # sell if below stoploss threshold
                print str(invested) + "===================================="
                print str(valueOnLastAction) + "================"
                if invested != 0:
                    self.actionCount += 1
                    myCash = invested - self.transactionCost
                    if myCash < valueOnLastAction:
                        myCash = myCash * (1 - self.punishment)
                        self.badTrades += 1
                    invested = 0
                    trades += 1
                    lastTrade = "Stop loss"
                    valueOnLastAction = myCash
                else:
                    lastTrade = "Stop loss"

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


    def benchmark(self):
        gu.log("Benchmarking " + str(self.historicalData))
        self.compute_fitness_score()
        startingShares = self.startingCash/self.historicalData[self.lookback]["close"]
        marketValue = startingShares * self.historicalData[len(self.historicalData)-1]["close"]

        result = "starting money: " + str(self.startingCash) + "\n" +\
        "share value: " + str(self.historicalData[self.lookback]["close"]) + " on " + str(self.historicalData[self.lookback]["date"]) + "\n" +\
        "share value: " + str(self.historicalData[len(self.historicalData)-1]["close"]) + " on " + str(self.historicalData[len(self.historicalData)-1]["date"])+ "\n" +\
        "profit: " + str(self.profit) + "\n" +\
        "Buy + hold profit: " + str(marketValue - self.startingCash) + "\n" +\
        "Trade count: " + str(self.actionCount)

        if self.startingCash + self.profit > marketValue:
            result += ("\n ------------------------ MONEY")

        return result


    def compute_options_fitness_score(self):

        self.actionCount = 0
        self.badTrades = 0
        shortLoan = 0
        loanInterest = self.marginInterest
        shortedShares = 0
        trades = 0
        myCash = self.startingCash
        invested = 0
        valueOnLastAction = self.startingCash
        dayCounter = 0

        for dayIndex in range(self.lookback, len(self.historicalData)):
            lastTrade = "NULL"
            invested = invested * (1 + self.historicalData[dayIndex]["dayChange"])  # update value of investments


            dayCounter +=1
            if dayCounter >= 21:
                #gu.log("DEBUG: Loan update from: " + str(shortLoan))
                shortLoan = shortLoan * (1 - loanInterest)  #update for approximate monthly penalty compounding
                #gu.log("DEBUG: Loan update to: " + str(shortLoan))

            portfolioValue = invested + myCash #one of these values will be zero so it will just hold the actual protfolio value

            dayBuyStrength = 0
            daySellStrength = 0
            for indicator in self.constraints[0]:
                value = self.historicalData[dayIndex][indicator]
                contstraintBuyTriggers = 0
                contstraintSellTriggers = 0
                for day in range(self.lookback):
                    if self.constraints[day][indicator]["BuyUpper"] > value > self.constraints[day][indicator][
                        "BuyLower"]:
                        contstraintBuyTriggers += 1
                    if self.constraints[day][indicator]["SellUpper"] > value > self.constraints[day][indicator][
                        "SellLower"]:
                        contstraintSellTriggers += 1
                if contstraintBuyTriggers - contstraintSellTriggers >= self.lookbackThreshold:
                    dayBuyStrength += (1 * self.constraints[day][indicator]["BuyWeight"])
                elif contstraintSellTriggers - contstraintBuyTriggers >= self.lookbackThreshold:
                    daySellStrength += (1 * self.constraints[day][indicator]["SellWeight"])

            self.buysellScores = [dayBuyStrength, daySellStrength]
            # count up lookback signals
            if (dayBuyStrength - daySellStrength) >= self.triggerThreshold:
                if myCash != 0:
                    self.actionCount += 1
                    if shortedShares > 0:               # cover position
                        marketvalue = shortedShares * self.historicalData[dayIndex]["close"]
                        shortProfit = shortLoan - marketvalue
                        myCash += shortProfit
                        shortedShares = 0.0
                        shortLoan = 0.0

                        #debug = ("DEBUG: short profit: " + str(shortProfit))
                        #if shortProfit > 0:
                        #    debug += "**********"
                        #    gu.log(debug)

                    invested = myCash - self.transactionCost
                    if invested < valueOnLastAction:
                        invested = invested * (1 - self.punishment)
                        self.badTrades += 1
                    myCash = 0
                    trades += 1
                    lastTrade = "BUY/COVER"
                    valueOnLastAction = invested
                else:
                    lastTrade = "BUY/COVER"

            elif (daySellStrength - dayBuyStrength) >= self.triggerThreshold:
                if invested != 0:
                    self.actionCount += 1
                    myCash = invested - self.transactionCost
                    if myCash < valueOnLastAction:
                        myCash = myCash * (1 - self.punishment)
                        self.badTrades += 1
                    invested = 0
                    trades += 1
                    lastTrade = "SELL/SHORT"
                    valueOnLastAction = myCash
                else:
                    lastTrade = "SELL/SHORT"

                #gu.log(shortLoan)

                if shortLoan == 0.0:
                    #gu.log("DEBUG: shorting")
                    shortLoan = portfolioValue * self.shortRatio
                    #gu.log("DEBUG: Loan: " + str(shortLoan))
                    shortedShares = shortLoan/float(self.historicalData[dayIndex]["close"])
                    #gu.log("DEBUG: shares: " + str(shortedShares))

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
            profitPerTrade = profit / float(trades)
        else:
            profitPerTrade = 0
        if self.Debug: gu.log("Average profit per trade: " + str(profitPerTrade))

        if trades > 0:
            self.fitnessScore = profit

        if lastTrade != "":
            self.finalTrade = lastTrade

        if self.actionCount > 0:
            self.relativeCorrectness = 1 - (float(self.badTrades) / float(self.actionCount))