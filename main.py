__author__ = 'Cameron'
import GiroUtilities as gu
import LineageClass
import GIROControllerClass

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

    GIRO = GIROControllerClass.GiroController("results", "StockData/stocksToAnalyze.txt")
    GIRO.init_stock_list()
    GIRO.giro_start()


main()