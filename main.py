__author__ = 'Cameron'
import GiroUtilities as gu
import GIROControllerClass

'''
    TODO:
        Need to expand options included in config file
        add in self test of predictive capabilities

        Need to start thinking about delegating these actions out to the GIROcontroller
            - system analysis should also be done in main
            - all real computation/setup/system control should be done in the controller
'''

def main():
    gu.log("Initializing Project GIRO...")

    GIRO = GIROControllerClass.GiroController("results", "StockData/stocksToAnalyze.txt", "configs/giroConfig.txt")
    GIRO.init_stock_list()
    GIRO.get_settings()
    GIRO.giro_start()


main()