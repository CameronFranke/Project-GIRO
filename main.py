__author__ = 'Cameron'
import GiroUtilities as gu
import LineageClass

'''
    TODO:
        Need to build in XML style config file ASAP
            - or simple ':' separated param file
'''

def main():
    gu.log("Initializing Project GIRO...")

    technicalIndicators = ["SMA", "MACD", "BBANDS", "dayChange"]
    triggerThreshold = .70
    dayTriggerThreshold = .70
    lookbackLevel = 3
    generations = 1
    populatioSize = 1
    dateRange = {}
    dateRange["startM"] = "01"
    dateRange["startD"] = "01"
    dateRange["startY"] = "2010"
    dateRange["stopM"] = "12"
    dateRange["stopD"] = "31"
    dateRange["stopY"] = "2014"

    x = LineageClass.Lineage("GOOG", dateRange, technicalIndicators, populatioSize, generations, lookbackLevel, triggerThreshold, dayTriggerThreshold)
    x.pull_Yahoo_Finance_Data()
    x.compute_technical_indicators()
    #x.print_Raw_Data()
    x.compute_indicator_ranges()
    x.initialize_population()
    x.population[0].print_constraints()
    #x.population[0].compute_fitness_score()


main()