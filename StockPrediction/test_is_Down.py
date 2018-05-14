import http.client, urllib
import os
import sqlalchemy as sa
import pandas as pd
import datetime as dt
import numpy as np

def test_down(date_after,bar,count):
    d1 = dt.datetime.now()
    engine = sa.create_engine('mysql://kevin:@127.0.0.1/Stock?charset=utf8') # 123.206.69.99 server
    stock_df = pd.read_sql_query("select distinct code from stock_price_test_allfeature;",engine)
    stock_s = pd.Series(stock_df['code']).sort_values()
    stock_list = stock_s.tolist()
    counter = 0
    for i in stock_list:
        counter = counter+1
        # print(i)
        # list = []
        # list2= []
        sql = "SELECT * FROM stock_price_test_allfeature WHERE stockname = "+i+" ORDER BY date;"
        stock_price_df = pd.read_sql_query(sql,engine)
        # print(stock_price_df)
        # stock_price_UD = pd.DataFrame(np.zeros((stock_price_df.shape[0],1)),columns=['UpOrDown'])
        # stock_price_UD['UpOrDown']=False
        # print(stock_price_df)
        stock_price_df.pop('level_0')
        stock_price_df.pop('index')
        iD = pd.DataFrame(np.zeros((stock_price_df.shape[0],1)),columns=['isDown'])
        iD['isDown'] = False
        # stock_price_df['isDown']=0
        # iD = np.array(sto)
        row_number = stock_price_df.shape[0]
        for j in range(0, row_number):
            if(j<2):
                continue
            elif(stock_price_df.iloc[j-2].high*0.95>stock_price_df.iloc[j].open):
                iD.iloc[j].isDown = True
                # stock_price_df.iloc[j].isDown = 1
                # print(stock_price_df.iloc[j].code)
                # print()
            else:
                continue
            # if j + 3> row_number:
            #     # print(j)
            #     break
            # else:
            #     sub_df = stock_price_df.iloc[j:j+3]
            #     # print(sub_df)
            #     # print(sub_df.iloc[2].high)
            #     if(sub_df.iloc[0].high*0.95 > sub_df.iloc[2].open):
            #         stock_price_df.isDown.iloc[j+2]=True
                    # if((1.15*sub_df.iloc[3].low) < sub_df.iloc[4:16].high.max()):
                    #     list2.append(j+2)
                        # counter +
        # stock_price_UD['UpOrDown'].loc[list2]=True
        # print(stock_price_UD.loc[list2])
        # list.append(j)

        # else:
        #     counter += 1
        #     list.append(j+2)
        # print('1')
        # print(stock_price_UD.loc[list2])
        # stock_price_df.insert(stock_price_df.shape[1],'UpOrDown',stock_price_UD)
        stock_price_df.insert(stock_price_df.shape[1],'isDown',iD)
        # print(stock_price_df)
        # print(stock_price_UD[stock_price_UD['UpOrDown']==True])
        stock_price_df[stock_price_df.date>=date_after].to_sql('stock_price_test_down',engine,if_exists='append')
        bar.update(count+counter)


        # stock_price_df.iloc[list].to_sql('stock_label_3d',engine,if_exists='append')



    print("total number: ")
    print(counter)
    d2 = dt.datetime.now()
    print("time used: ")
    print(d2-d1)
    print_str = "total number: "+str(counter)+"\ntime used: "+str(d2-d1)

    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
      urllib.parse.urlencode({
        "token": "a22vgia8q7vszh4zromzgd2jgikxeh",
        "user": "u6xu8s5vtjz982g9btzrfzm1r6e2q8",
        "message": "done ！\n"+print_str,
        "title":os.path.basename(__file__),
      }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    return len(stock_list)
