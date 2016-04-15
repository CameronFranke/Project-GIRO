__author__ = 'Cameron'
import GiroUtilities as gu
import GIROControllerClass
from time import time

'''
    TODO:
        Need to expand options included in config file
        add in self test of predictive capabilities

        Need to start thinking about delegating these actions out to the GIROcontroller
            - system analysis should also be done in main
            - all real computation/setup/system control should be done in the controller
'''

def main():
    #gu.pull_stock_list()
    gu.create_log_file()
    gu.log("Initializing Project GIRO...")
    start = time()
    GIRO = GIROControllerClass.GiroController("Logs/results.txt", "configs/stocksToAnalyze.txt", "configs/giroConfig.txt")
    GIRO.init_stock_list()
    GIRO.get_settings()
    GIRO.giro_start()
    stop = time()
    gu.log("GIRO total execution time: " + str(stop - start))

main()