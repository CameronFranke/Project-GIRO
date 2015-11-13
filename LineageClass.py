__author__ = 'Cameron'
import GiroUtilities as gu

class Lineage():

    def __init__(self, stockSymbol, populationSize, generationCount):

        self.symbol = stockSymbol
        self.populationSize = populationSize
        self.population = []
        self.generationCount = generationCount
