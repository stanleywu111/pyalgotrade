# -*- coding:utf-8 -*-

from WindPy import w
import pandas as pd
import datetime
import os
w.start();

# get stock list
stockList = w.wset("sectorconstituent","date=2016-08-17;sectorid=a001010100000000")
stockList = stockList.Data[1]

# get unlisted stock list
unlistedStockList = w.wset("sectorconstituent","date=2016-08-17;sectorid=a001010m00000000")
unlistedStockList = unlistedStockList.Data[1]


def wind2csv(sid, startDate = "2005-01-04", endDate = "2016-8-16"):
    wsd_data=w.wsd(sid, "pre_close,open,high,low,close,volume,amt,dealnum,pct_chg,swing,vwap,adjfactor,turn,trade_status,susp_reason,maxupordown", startDate, endDate, "PriceAdj=F")
    #wsd_data.Fields.insert(0,'Date')
    for i in range(0,len(wsd_data.Times)):
        wsd_data.Times[i] = wsd_data.Times[i].date()
    fm=pd.DataFrame(wsd_data.Data,index=wsd_data.Fields,columns=wsd_data.Times)
    fm = fm.T
    fm.index.name='DATE'
    filename = sid[0:6]+'.csv'
    fm.to_csv(os.path.join(r'E:\Personal\pyalgotrade\data', filename),encoding='utf-8')


for i in range(0, len(stockList)):
    wind2csv(stockList[i])
    print i

for i in range(0, len(unlistedStockList)):
    wind2csv(unlistedStockList[i])
    print i



#get HS300Weight
import pandas as pd







