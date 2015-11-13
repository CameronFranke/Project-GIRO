__author__ = 'Cameron'
import GiroUtilities as gu
import LineageClass

def main():
    gu.log("test")
    x = LineageClass.Lineage("GOOG", 1, 1)
    x.pullYahooFinanceData()



main()