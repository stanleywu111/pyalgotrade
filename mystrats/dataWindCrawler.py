# -*- coding:utf-8 -*-

from WindPy import w
import pandas as pd
import datetime
import os
w.start();

def wind2csv(sid, startDate = "2005-01-04", endDate = "2016-8-15"):
    wsd_data=w.wsd(sid, "open,high,low,close", startDate, endDate, "Fill=Previous")
    fm=pd.DataFrame(wsd_data.Data,index=wsd_data.Fields,columns=wsd_data.Times)
    fm = fm.T
    filename = sid[0:6]+'.csv'

    fm.to_csv(os.path.join(r'E:\Personal\pyalgotrade\data', filename))




