import http.client, urllib
import os
import datetime as dt
import time
import sqlalchemy as sa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import talib as ta
Notifi = True
result = None

def test_feature(date_after,bar,count):
    d1 = dt.datetime.now()

    engine = sa.create_engine('mysql://root:root@localhost/stocktool?charset=utf8')
    stock_df = pd.read_sql_query("select DISTINCT code from stockprediction_stock_price;",engine)
    stock_s = pd.Series(stock_df['code']).sort_values()
    stock_list = stock_s.tolist()
    counter = 0

    # print(counter)
    for i in stock_list:
        counter += 1
        # print(str(counter)+"\t"+i)
        # sql_price = "SELECT * FROM stockprediction_stock_price WHERE code = "+i+" and date > (select date from stockprediction_stock_price where code = '000001' order by date desc limit 37,1) ORDER BY date;"
        sql_price = "SELECT * FROM stockprediction_stock_price WHERE code = "+i+" and date > '2018-04-01' ORDER BY date;"
        price_data = pd.read_sql(sql_price,engine)
        if(price_data.empty):
            print(i)
        else:
            macd,macds,price_data['macdh']      =ta.MACD(price_data['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
            price_data['stoK'],price_data['stoD']                           =ta.STOCH(price_data['high'].values,price_data['low'].values,price_data['close'].values)
            price_data['rsi']                                               =ta.RSI(price_data['close'].values)
            price_data['willR']                                             =ta.WILLR(price_data['high'].values,price_data['low'].values,price_data['close'].values)
            price_data['ultosc']                                            =ta.ULTOSC(price_data['high'].values,price_data['low'].values,price_data['close'].values)
            price_data['mfi']                                               =ta.MFI(price_data['high'].values,price_data['low'].values,price_data['close'].values,price_data['volume'].values)
            # price_data.pop('level_0')
            # price_data.pop('index')
            # print(price_data[price_data.date<'2018-04-16'])
            # price_data[price_data.date>=date_after].to_sql('stockprediction_stock_pred',engine,if_exists='append',index=False)
            price_data.pop('id')
            """ is down"""
            iD = pd.DataFrame(np.zeros((price_data.shape[0], 1)), columns=['down'])
            iD['down'] = False
            row_number = price_data.shape[0]

            for j in range(0,row_number):
                if(j<2):
                    continue
                elif(price_data.iloc[j-2].high*0.95>price_data.iloc[j].open):
                    iD.iloc[j].down = True
                else:
                    continue
            price_data.insert(price_data.shape[1],'down',iD)
            """ end down"""
            price_data[price_data.date>=dt.datetime.strptime(date_after,'%Y-%m-%d').date()].to_sql('stockprediction_stock_pred',engine,if_exists='append',index=False)
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