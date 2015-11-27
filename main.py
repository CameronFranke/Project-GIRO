__author__ = 'Cameron'
import GiroUtilities as gu
import LineageClass

'''
    TODO:
        Need to build in XML style config file ASAP
            - or simple ':' separated param file

        Need to start thinking about delegating these actions out to the GIROcontroller
            - XML/ parameters read should be done in main
            - system analysis shoudl also be done in main
            - all real computation/setup/system control should be done in the controller
'''

def main():
    gu.log("Initializing Project GIRO...")

    technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange"]

    triggerThreshold = .30
    dayTriggerThreshold = .50

    lookbackLevel = 3

    generations = 3
    populationSize = 8

    selectionPercentage = .75

    dateRange = {}
    dateRange["startM"] = "00"
    dateRange["startD"] = "01"
    dateRange["startY"] = "2010"
    dateRange["stopM"] = "11"
    dateRange["stopD"] = "31"
    dateRange["stopY"] = "2015"

    x = LineageClass.Lineage("GOOG",
                                 dateRange,
                                 technicalIndicators,
                                 populationSize,
                                 generations,
                                 lookbackLevel,
                                 triggerThreshold,
                                 dayTriggerThreshold,
                                 selectionPercentage)

    x.master_initialize()
    recommendation = x.evolve()
    gu.log("Recommendation: " + recommendation)

main()