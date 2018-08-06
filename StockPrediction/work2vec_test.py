from sqlalchemy import create_engine
import pandas as pd
import os
import shutil
import datetime as dt
import time
import tushare
from gensim.models import word2vec
import gensim
import logging
"""
word2vec模型相关操作，训练模型时需要使用，训练完成后就没用了，所有模块都封装成了函数，可根据需要进行调用
chan_cal与train_todatabase都只是数据的插入，需要根据实际进行手动的相应的数据删除，才能正常工作
单次训练结果储存在stock_change.model文件，多次训练结果储存在multi_train.model
"""
engine = create_engine('mysql://gupiao:gupiao@localhost/stocktool?charset=utf8') # 123.206.69.99 server
def change_cal(engine, start_date): #计算股票涨幅,储存到表StockPrediction_stock_change,计算start_date之后的所有数据
    stock_df = pd.read_sql_query("select code,name from stock_list;",engine)# stock_list是指股票列表 记录所有股票的代码以及名称，用于遍历股票代码
    stock_s = pd.Series(stock_df['code']).sort_values()
    list1=stock_s.tolist();
    stock_list = sorted(set(list1), key=list1.index);
    price_yestoday = 0.0;
    for i in stock_list:
        sql_data = "select date,code,close,stockname from StockPrediction_stock_price where date >= '%s' and code = %s" % (start_date, str(i));
        stock_data = pd.read_sql_query(sql_data, engine);
        if(stock_data.empty):
            pass;
        else:
            price_yestoday = stock_data.iloc[[0]].close;
            change = [];
            for j in range(1,stock_data.count().date):
                price_today = stock_data.iloc[[j]].close;
                change.append(float(float(price_today)/float(price_yestoday) - 1));
                price_yestoday = price_today;
            stock_data.drop([0],inplace=True);
            stock_data['price_change'] = change;
            stock_data[['code', 'stockname', 'date', 'price_change']].to_sql('StockPrediction_stock_change',engine,if_exists='append',index=False);
    return ;
#change_cal(engine,'2018-07-01');
def data_transform(engine): #根据StockPrediction_stock_change数据，进行统计转换得到训练模型所需数据
    fp = open("data/stock_change.txt", 'w+',  encoding='utf-8');
    sql_sel = "select date,price_change from StockPrediction_stock_change";
    data = pd.read_sql_query(sql_sel, engine);
    high_change = float(data.price_change.max());
    low_change = float(data.price_change.min());
    lea_change = low_change;
    high_date = dt.datetime.strptime(str(data.date.max()),'%Y-%m-%d');
    low_date = dt.datetime.strptime(str(data.date.min()),'%Y-%m-%d');
    lea_date = low_date;
    while lea_date <= high_date:
        print(lea_date)
        while lea_change < high_change:
            sql_sel2 = "select code from StockPrediction_stock_change where date = '%s' and price_change >= %s and price_change < %s" % (lea_date.strftime('%Y-%m-%d'), str(lea_change), str(lea_change+0.02));
            data2 = pd.read_sql_query(sql_sel2, engine);
            if(data2.empty):
                pass;
            else:
                labnel = "%s_%5.4f~%5.4f  " % (lea_date.strftime('%Y-%m-%d'), lea_change, lea_change+0.02);
                fp.write(labnel);
                data_code = pd.Series(data2['code']).tolist();
                data_code.sort()
                for s in data_code:
                    fp.write(s+' ')
                fp.write('\n')
            lea_change += 0.01;
        lea_change = low_change;
        lea_date += dt.timedelta(days=1);
    fp.close();
    return ;


def model_train(train_file_name, save_model_file): 
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO);
    sentences = word2vec.Text8Corpus(train_file_name);  # 加载语料
    model = gensim.models.Word2Vec(sentences, size=200, window=5, min_count=2);  # 训练skip-gram模型; 默认window=5
    model.save(save_model_file);
    model.wv.save_word2vec_format(save_model_file + ".bin", binary=True);

#model_train('data/stock_change.txt','data/stock_change.model'); #训练模型




def multi_train(engine):  #采用多次训练的方式进行模型训练
    sql_sel = "select date,price_change from StockPrediction_stock_change";
    data = pd.read_sql_query(sql_sel, engine);
    high_change = float(data.price_change.max());
    low_change = float(data.price_change.min());
    lea_change = low_change;
    high_date = dt.datetime.strptime(str(data.date.max()), '%Y-%m-%d');
    low_date = dt.datetime.strptime(str(data.date.min()), '%Y-%m-%d');
    lea_date = low_date;


    fp = open("data/multi_train.txt", 'w+', encoding='utf-8');
    print(lea_date)
    while lea_change < high_change:
        sql_sel2 = "select code from StockPrediction_stock_change where date = '%s' and price_change >= %s and price_change < %s" % (
            lea_date.strftime('%Y-%m-%d'), str(lea_change), str(lea_change + 0.02));
        data2 = pd.read_sql_query(sql_sel2, engine);
        if (data2.empty):
            pass;
        else:
            labnel = "%5.4f~%5.4f  " % (lea_change, lea_change + 0.02);
            fp.write(labnel);
            data_code = pd.Series(data2['code']).tolist();
            for s in data_code:
                fp.write(s + ' ')
            fp.write('\n')
        lea_change += 0.01;
    fp.close();
    lea_change = low_change;
    lea_date += dt.timedelta(days=1);
    model_train('data/multi_train.txt','data/multi_tmp.model');
    model = word2vec.Word2Vec.load('data/multi_tmp.model');
    m = model.wv;


    while lea_date <= high_date:
        print(lea_date)
        if (tushare.is_holiday(lea_date.strftime('%Y-%m-%d'))):
            lea_date += dt.timedelta(days=1);
            print('yes')
            pass;
        else:
            fp = open("data/multi_train.txt", 'w+', encoding='utf-8');
            while lea_change < high_change:
                sql_sel2 = "select code from StockPrediction_stock_change where date = '%s' and price_change >= %s and price_change < %s" % (
                lea_date.strftime('%Y-%m-%d'), str(lea_change), str(lea_change + 0.02));
                data2 = pd.read_sql_query(sql_sel2, engine);
                if (data2.empty):
                    pass;
                else:
                    labnel = "%5.4f~%5.4f  " % (lea_change, lea_change + 0.02);
                    fp.write(labnel);
                    data_code = pd.Series(data2['code']).tolist();
                    data_code.sort()
                    for s in data_code:
                        fp.write(s + ' ')
                    fp.write('\n')
                lea_change += 0.01;
            fp.close();
            lea_change = low_change;
            lea_date += dt.timedelta(days=1);
            model_train('data/multi_train.txt','data/multi_tmp.model');
            model = word2vec.Word2Vec.load('data/multi_tmp.model');
            m2 = model.wv;
            for o in m.index2word:
                if(o in m2.index2word):
                    m[str(o)] = m[str(o)] + m2[str(o)];
    model.save("data/multi_train.model");
    y2 = m.most_similar("000001", topn=10)  # 10个最相关的

    print(u"000001最相关的股票有：\n")
    for item in y2:
        print(item[0], item[1])
    print("-------------------------------\n")

    return;
"""                       #用于测试准确度
#multi_train(engine);
moudle1 = word2vec.Word2Vec.load("data/multi_train.model")
print(moudle1)
print(moudle1.wv.index2word)
y2 = moudle1.most_similar("002222", topn=1)  # 10个最相关的
print(y2[0][0])
print(u"3005585最相关的股票有：\n")
for item in y2:
    print(item[0], item[1])
print("-------------------------------\n")

#data_transform(engine);
#model_train('data/stock_change.txt','data/stock_change.model');
moudle1 = word2vec.Word2Vec.load("data/stock_change.model")
print(moudle1)
y2 = moudle1.most_similar("000005", topn=10)  # 10个最相关的

print(u"000001最相关的股票有：\n")
for item in y2:
    print(item[0], item[1])
print("-------------------------------\n")
"""


def train_todatabse(engine):  #根据训练好的模型进行查询并把相关数据储存到StockPrediction_stock_similar
    sql1 = "select code,stockname from StockPrediction_stock_change";
    data = pd.read_sql_query(sql1,engine).drop_duplicates();
    code_list = pd.Series(data['code']).tolist();
    code_list.sort();
    modle1 = word2vec.Word2Vec.load("/home/buaa/Documents/gupiaoyuce/StockPrediction/data/multi_train.model");
    code_have = modle1.wv.index2word;
    similar_code = [];
    similar_name = [];
    similar_rate = [];
    for code in code_list:
        if(code in code_have):
            y = modle1.most_similar(code, topn=1);
            similar_code.append(y[0][0]);
            similar_rate.append(y[0][1]);
            a = data[data.code == code].values.tolist();
            similar_name.append(a[0][1])
        else:
            similar_name.append('0');
            similar_code.append('0');
            similar_rate.append(0);
    data['similar_code'] = similar_code;
    data['similar_name'] = similar_name;
    data['similar_rate'] = similar_rate;
    data[data.similar_code != '0'].to_sql('StockPrediction_stock_similar',engine, if_exists='append', index=False);
