import sys
import os
import numpy as np
import math

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.stratanalyzer import returns
from pyalgotrade.barfeed import myfeed
from pyalgotrade.technical import ma

from cvxpy import *

def price2return(prices):
    returns = [(x_y[1]/x_y[0])-1 for x_y in zip(prices[0:-1], prices[1:])]
    return returns

def portOpt(ret,n):
    cov = np.cov(ret)
    weights = []
    if np.isnan(cov).any() == False:
        w = Variable(n)
        risk = quad_form(w, cov)
        prob = Problem(Minimize(risk),[sum_entries(w) == 1])
        prob.solve()
        for weight in w.value:
            weights.append(float(weight[0]))
    return weights


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instruments):
        super(MyStrategy, self).__init__(feed)
        self.__instruments = instruments
        self.setUseAdjustedValues(False)
        self.__rebalanceMonth = None
        self.__sharesToBuy = {}
        self.__sma = {}
        self.__priceDS= {}
        for inst in instruments:
            self.__priceDS[inst]  = feed[inst].getPriceDataSeries()
            self.__priceDS[inst].setMaxLen(20)
            self.__sma[inst] = ma.SMA(self.__priceDS[inst], 200)

    def getSMA(self):
        return self.__sma

    def _shouldRebalance(self, dateTime):
        return dateTime.month != self.__rebalanceMonth

    def _rebalance(self):
        self.info("Rebalancing")

        for order in self.getBroker().getActiveOrders():
            self.getBroker().cancelOrder(order)

        curPos = self.getBroker().getPositions()

        for inst in self.__instruments:
            num = curPos.get(inst)
            if num is not None:
                self.marketOrder(inst,-num, goodTillCanceled=True)

        equity = self.getBroker().getEquity()
        data = [np.array(price2return(self.__priceDS[inst].getPrice())) for inst in self.__instruments]
        weights = portOpt(data,len(self.__instruments))
        if len(weights) > 0:
            for i in range(len(self.__instruments)):
                pri = self.__priceDS[self.__instruments[i]].getPrice()[-1]
                num = math.floor(equity*weights[i]/pri)
                self.marketOrder(self.__instruments[i], num, goodTillCanceled=True)
         
    def onBars(self, bars):
        currentDateTime = bars.getDateTime()

        #print currentDateTime
        #for inst in self.__instruments:
        #    print "s ", type(self.__priceDS[inst].getPrice())

        if self._shouldRebalance(currentDateTime):
            self.__rebalanceMonth = currentDateTime.month
            print("REBALANCING {0}".format(currentDateTime))
            self._rebalance()
           
            

# Load the yahoo feed from the CSV file
instruments = ['000001', '600305', '000006']

feed = myfeed.Feed()

for inst in instruments:
    filename = inst +'.csv'
    feed.addBarsFromCSV(inst, os.path.join(r'E:\Personal\pyalgotrade\data\dailybar', filename))

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, instruments)
returnsAnalyzer = returns.Returns()
myStrategy.attachAnalyzer(returnsAnalyzer)
plt = plotter.StrategyPlotter(myStrategy)
myStrategy.run()
plt.plot()
