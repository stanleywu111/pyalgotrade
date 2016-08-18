# -*- coding:utf-8 -*-

from pyalgotrade import strategy
from pyalgotrade import plotter
from pyalgotrade.barfeed import myfeed

import os


class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, instrument):
        super(MyStrategy, self).__init__(feed)
        self.__instrument = instrument

    def onBars(self, bars):
        bar = bars[self.__instrument]
        self.info(bar.getClose())


feed = myfeed.Feed()
feed.addBarsFromCSV("PingAn", "000001.csv")

myStrategy = MyStrategy(feed, "PingAn")
myStrategy.run()



