__author__ = 'Cameron'
import GiroUtilities as gu
import LineageClass

def main():

    technicalIndicators = ["SMA"]
    dateRange = {}
    dateRange["startM"] = "01"      # Need to build in XML style config file ASAP
    dateRange["startD"] = "01"
    dateRange["startY"] = "2010"
    dateRange["stopM"] = "12"
    dateRange["stopD"] = "31"
    dateRange["stopY"] = "2014"

    x = LineageClass.Lineage("GOOG", dateRange, technicalIndicators, 1, 1)
    x.pull_Yahoo_Finance_Data()
    #x.printRawData()
    x.compute_technical_indicators()
    x.print_Raw_Data()


main()