import http.client, urllib
import os
import datetime as dt

import sqlalchemy as sa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as ta
Notifi = True
result = None

def test_feature(date_after,bar,count):
    d1 = dt.datetime.now()

    engine = sa.create_engine('mysql://kevin:@localhost/Stock?charset=utf8')


    stock_df = pd.read_sql_query("select DISTINCT code from stock_price_test;",engine)
    stock_s = pd.Series(stock_df['code']).sort_values()
    stock_list = stock_s.tolist()
    counter = 0
    # print(counter)
    for i in stock_list:
        counter += 1
        # print(str(counter)+"\t"+i)
        sql_price = "SELECT * FROM stock_price_test WHERE code = "+i+" ORDER BY date;"
        price_data = pd.read_sql(sql_price,engine)
        price_data['macd'],price_data['macds'],price_data['macdh']      =ta.MACD(price_data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        price_data['upperBB'],price_data['midBB'],price_data['lowBB']   =ta.BBANDS(price_data['close'].values)
        price_data['stoK'],price_data['stoD']                           =ta.STOCH(price_data['high'].values,price_data['low'].values,price_data['close'].values)
        price_data['rsi']                                               =ta.RSI(price_data['close'].values)
        price_data['atr']                                               =ta.ATR(price_data['high'].values,price_data['low'].values,price_data['close'].values)
        price_data['willR']                                             =ta.WILLR(price_data['high'].values,price_data['low'].values,price_data['close'].values)
        price_data['trix']                                              =ta.TRIX(price_data['close'].values)
        price_data['ultosc']                                            =ta.ULTOSC(price_data['high'].values,price_data['low'].values,price_data['close'].values)
        price_data['storsiK'],price_data['storsiD']                     =ta.STOCHRSI(price_data['close'].values)
        price_data['roc']                                               =ta.ROC(price_data['close'].values)
        price_data['rocp']                                              =ta.ROCP(price_data['close'].values)
        price_data['rocr']                                              =ta.ROCR(price_data['close'].values)
        price_data['rocr100']                                           =ta.ROCR100(price_data['close'].values)
        price_data['mfi']                                               =ta.MFI(price_data['high'].values,price_data['low'].values,price_data['close'].values,price_data['volume'].values)
        # price_data.pop('level_0')
        # price_data.pop('index')
        # print(price_data[price_data.date<'2018-04-16'])
        price_data[price_data.date>=date_after].to_sql('stock_price_test_allfeature',engine,if_exists='append')
        # print(counter)
        bar.update(count+counter)
        # price_data.to_sql('stock_price_test_allfeature',engine,if_exists='append')
        # print(price_data)
    # macd=ta.MACD(price_data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    # sql_price = "SELECT * FROM stock_price_k WHERE code = "+'300001'+";"
    # price_data = pd.read_sql(sql_price,engine)
    # price_data['macd'],price_data['macds'],price_data['macdh']=ta.MACD(price_data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    # print(price_data)
    # price_data.to_sql('stock_price_k_all',engine,if_exists='append')
    # 最终手机提示
    if(Notifi):
        d2 = dt.datetime.now()
        print("time used: ")
        print(d2 - d1)
        print_str = "\ntime used: " + str(d2 - d1)
        if(result is not None):
            msg = "done ！\n" + print_str+"\nresult: "+str(result)
        else:
            msg = "done ！\n" + print_str
        conn = http.client.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
                     urllib.parse.urlencode({
                         "token": "a22vgia8q7vszh4zromzgd2jgikxeh",
                         "user": "u6xu8s5vtjz982g9btzrfzm1r6e2q8",
                         "message": msg,
                         "title": os.path.basename(__file__),
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        conn.getresponse()
    return len(stock_list)