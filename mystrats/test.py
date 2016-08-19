from pyalgotrade import strategy
from pyalgotrade.barfeed import myfeed

import os



class MyStrategy(strategy.BacktestingStrategy):
    def __init__(self, feed, *instruments):
        super(MyStrategy, self).__init__(feed)

    def onBars(self, bars):
        for inst in instruments:
            bar = bars[inst]
            self.info(bar.getClose())


# Load the yahoo feed from the CSV file
instruments = ['000001', '600000', '000002']

feed = myfeed.Feed()

for inst in instruments:
    filename = inst +'.csv'
    feed.addBarsFromCSV(inst, os.path.join(r'E:\Personal\pyalgotrade\data\dailybar', filename))

# Evaluate the strategy with the feed's bars.
myStrategy = MyStrategy(feed, instruments[0], instruments[1])
myStrategy.run()
