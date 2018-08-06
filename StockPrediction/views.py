from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout
from datetime import timedelta,date
import datetime as dt
# Create your views here.
from StockPrediction import models
import sqlalchemy as sa
import tushare as ts
import pandas as pd
from django.utils import timezone
from django.db import connection
from django.http import JsonResponse
import json
from gensim.models import word2vec
import gensim
class winrate:
    date = ''
    rate = ''
def index(req):
    t = 'ABVC'
    return render(req, 'index.html', {'t': t})


def user_index(req):
    username = req.user.username
    return render(req,'user_index.html',{'username':username})

def signup(req):
    if req.method == 'POST':
        form = UserCreationForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect('/signup')
    else:
        form = UserCreationForm()
    return render(req, 'signup.html', {'form': form})


def log_in(req):
    if req.method == 'POST':
        form = AuthenticationForm(data = req.POST)
        if form.is_valid():
            user = form.get_user()
            login(req, user)
            return redirect('/stockpred')
    else:
        form = AuthenticationForm()
    return render(req,'login.html',{'form':form,'username':req.user.username})

def log_out(req):
    if req.method == 'POST':
        logout(req)
        return redirect('/login')

def mana(req):
    if req.user.is_authenticated:
        if req.method == 'POST':
            engine = sa.create_engine('mysql://gupiao:gupiao@127.0.0.1/stocktool?charset=utf8')
            str = 'select * from stock_price_test where date = "2018-04-12" and code = "000014";'
            sp = pd.read_sql_query(str,engine)
            sp.pop('index')
            sp[['date','open','high','close','low','code','stockname','volume']].to_sql('StockPrediction_stock_price',engine,if_exists='append',index=False)
            # models.StockPrice.objects.create(stockname=sp.stockname.iloc[0],date=sp.date.iloc[0],code=sp.code.iloc[0],high=sp.high.iloc[0],low=sp.low.iloc[0],open=sp.open.iloc[0],close=sp.close.iloc[0],volume=sp.volume.iloc[0])
            return redirect('/login')
        md = models.StockPrice.objects.values('date')
        return render(req,'manage.html',{'md':md,'username':req.user.username})
    else:
        return redirect('/login',{'msg':'请先登录'})
def stockprice(req):
    url = 'stockprice'
    if req.user.is_authenticated:
        msg = '';
        if req.method == 'POST':
            code = req.POST['code']
            date = req.POST['date']
            if (code == '' and date == ''):
                msg = '请输入想要查询的股票及日期'
                sps = None
            else:
                if(code !='' and date != ''):
                    sps = models.stock_price.objects.filter(code=code,date=date)
                elif (code != ''):
                    sps = models.stock_price.objects.filter(code=code).order_by('-date')
                else:
                    sps = models.stock_price.objects.filter(date=date)
                if sps.count() == 0:
                    msg = '没有此股票行情数据，请重新进行查询！'
        else:
            sps = None
        return render(req,'stockprice.html',{'sps':sps,'username':req.user.username,'msg':msg,'url':url})
    else:

        form = AuthenticationForm()
        return render(req,'login.html',{'form':form,'msg':'请先登录'})
        # return redirect('/login', {'msg':msg})
def stockpred(req):
    url = 'stockpred'
    if req.user.is_authenticated:
        cur = connection.cursor()
        sps = models.stock_pred.objects.filter(down = 1, date__range=(timezone.now()+timedelta(days=-15),timezone.now())).exclude(macdh__lt=0.6,macdh__gt=-1.2).exclude(macdh=None).order_by('-date');
        for sp in sps:
            cur.execute("""select open from StockPrediction_stock_pred where code =%s and date >= %s order by date asc""",[sp.code,sp.date])
            row = cur.fetchone()
            if row == None:
                sp.hopeopen = '-'
            else:
                sp.hopeopen = row[0]
                sp.hopesale = float(sp.hopeopen)*1.08
            # sp.hig
            sp.close = models.stock_pred.objects.filter(code=sp.code).order_by('-date')[0].close
            if(sp.hopeopen == '-'):
                sp.chg = '-'
            else:
                sp.chg = (float(sp.close)/float(sp.hopeopen) - 1)*100
        return render(req,'stockpred.html',{'sps':sps,'username':req.user.username,'url':url})
    else:
        form = AuthenticationForm()
        return render(req,'login.html',{'form':form,'msg':'请先登录'})
def relation_analyze(req):
    url = 'relation_analyze';
    if req.user.is_authenticated:
        cur = connection.cursor();
        sps = models.stock_similar.objects.all();
        return render(req,'relation_analyze.html',{'sps':sps,'username':req.user.username,'url':url})
    else:
        form = AuthenticationForm()
        return render(req,'login.html',{'form':form,'msg':'请先登录'})
def similar_detail(req):
    url = 'similar_detail';
    if req.user.is_authenticated:
        if req.method == "GET":
            code = req.GET.get('code');
            model = word2vec.Word2Vec.load("/home/buaa/Documents/gupiaoyuce/StockPrediction/data/multi_train.model");
            y = model.most_similar(str(code),topn=11);
            similar_code = [];
            similar_rate = [];
            for item in y:
                similar_code.append(str(item[0]));
                a = float(item[1]);
                a = a*100;
                s = "%2.4f%%" % a;
                similar_rate.append(s);
        else:
            similar_code = [];
            similar_rate = [];
        return render(req, 'similar_detail.html', {'similar_code': similar_code, 'similar_rate': similar_rate, 'code':code, 'username': req.user.username, 'url': url})
    else:
        form = AuthenticationForm()
        return render(req, 'login.html', {'form': form, 'msg': '请先登录'})
def trend(req):
    if req.user.is_authenticated:
        if req.method == "GET":
            code1 = req.GET.get('code1');
            code2 = req.GET.get('code2');
            res = [];
            engine = sa.create_engine('mysql://gupiao:gupiao@127.0.0.1/stocktool?charset=utf8')
            sql = "SELECT distinct date FROM StockPrediction_stock_change order by date"
            data = pd.read_sql_query(sql, engine);
            dates1 = pd.Series(data['date']).tolist();
            dates = [];
            for a in dates1:
                a.strftime('%Y-%m-%d');
                dates.append(str(a));
            date_max = data['date'].max().strftime('%Y-%m-%d');
            date_min = data['date'].min().strftime('%Y-%m-%d');
            sql1 = "select close FROM StockPrediction_stock_price where code=%s and date>='%s' and date<='%s'" % (code1, date_min, date_max);
            sql2 = "select close FROM StockPrediction_stock_price where code=%s and date>='%s' and date<='%s'" % (code2, date_min, date_max);
            code1_price = pd.Series(pd.read_sql_query(sql1,engine)['close']).tolist();
            code2_price = pd.Series(pd.read_sql_query(sql2, engine)['close']).tolist();
        else:
            dates = [];
            code1_price = [];
            code2_price = [];
        res.append(dates)
        res.append(code1_price);
        res.append(code2_price);
        res.append(code1);
        res.append(code2);
        return JsonResponse(res, safe=False)
    else:
        form = AuthenticationForm()
        return render(req, 'login.html', {'form': form, 'msg': '请先登录'})
def userfollow(req):
    ufs = models.user_follow.objects.filter(username=req.user.username).order_by('-buy_date')
    for i in ufs:
        i.high = models.stock_price.objects.filter(code=i.code,date=i.buy_date)[0].high
        i.is_success = 'no_suc'
        if(i.buy_price!=-1):
            i.change = ((i.high/i.buy_price)-1)*100
            if(i.change>8):
                i.is_success = 'is_suc'
        else:
            i.change = '-'
            i.is_success = 'unknown_suc'
        if(i.sale_date is None):
            i.sale_date = '-'
        if(i.sale_price is None):
            i.sale_price = '-'
        # print(tmp[0].high)
        # print(i.high)
    # i.models.user_follow.objects.all()
    return render(req,'userfollow.html',{'username':req.user.username,'ufs':ufs})

def predanal(req):
    url='predanal'
    pas = None
    pas = models.pred_anal_macdh.objects.filter(buydate__gt='2018-01-01').order_by('-buydate')
    for i in pas:
        i.chg = (i.chg-1)*100
    return render(req,'predanal.html',{'username':req.user.username,'pas':pas,'url':url})

def winrate_ajax(req):
    wrs = []
    dates = models.pred_anal_macdh.objects.filter(buydate__gt='2018-01-01').distinct().values('buydate').order_by('buydate')
    total_win_count=0
    total_lose_count=0
    for date in dates:
        date_str = date['buydate'].strftime('%Y-%m-%d')
        win_count = models.pred_anal_macdh.objects.filter(buydate=date_str, chg__gt=1.08).count()
        lose_count = models.pred_anal_macdh.objects.filter(buydate=date_str).exclude(chg__gt=1.08).count()
        rate = win_count/(win_count+lose_count)
        wrs.append([date_str,rate])
        total_win_count +=win_count
        total_lose_count +=lose_count
    print(total_win_count,total_lose_count)
    return JsonResponse(wrs,safe=False)
def total_wr_ajax(req):
    wrs = []
    win = models.pred_anal_macdh.objects.filter(buydate__gt='2018-01-01',chg__gt=1.08).count()
    lose = models.pred_anal_macdh.objects.filter(buydate__gt='2018-01-01',chg__lt=1.08).count()
    wrs.append({'value':win,'name':'预测成功' })
    wrs.append({'value':lose,'name':'预测失败' })
    print(win,lose)
    return JsonResponse(wrs,safe=False)
