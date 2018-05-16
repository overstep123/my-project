from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,logout
from datetime import timedelta,date
# Create your views here.
from StockPrediction import models
import sqlalchemy as sa
import pandas as pd
from django.utils import timezone
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
            engine = sa.create_engine('mysql://root:root@127.0.0.1/stocktool?charset=utf8')
            str = 'select * from stock_price_test where date = "2018-04-12" and code = "000014";'
            sp = pd.read_sql_query(str,engine)
            sp.pop('index')
            sp[['date','open','high','close','low','code','stockname','volume']].to_sql('stockprediction_stockprice',engine,if_exists='append',index=False)
            # models.StockPrice.objects.create(stockname=sp.stockname.iloc[0],date=sp.date.iloc[0],code=sp.code.iloc[0],high=sp.high.iloc[0],low=sp.low.iloc[0],open=sp.open.iloc[0],close=sp.close.iloc[0],volume=sp.volume.iloc[0])
            return redirect('/login')
        md = models.StockPrice.objects.values('date')
        return render(req,'manage.html',{'md':md,'username':req.user.username})
    else:
        return redirect('/login',{'msg':'请先登录'})
def stockprice(req):
    if req.user.is_authenticated:
        print(1)
        if req.method == 'POST':
            code = req.POST['code']
            date = req.POST['date']
            sps = models.stock_price.objects.filter(code=code,date=date)
        else:
            sps = None
        return render(req,'stockprice.html',{'sps':sps,'username':req.user.username})
    else:

        form = AuthenticationForm()
        return render(req,'login.html',{'form':form,'msg':'请先登录'})
        # return redirect('/login', {'msg':msg})
def stockpred(req):
    if req.user.is_authenticated:
        if req.method == 'POST':
            print(req.POST['code'])
            print(req.POST['date'])
            price = models.stock_price.objects.filter(code=req.POST['code'],date=req.POST['date'])[0].open
            models.user_follow.objects.create(buy_date=req.POST['date'],code=req.POST['code'],username=req.user.username,buy_price=price)
        sps = models.stock_pred.objects.filter(down=True,macdh__range=(0.8,99),date__range=(timezone.now()+timedelta(days=-7),timezone.now())).order_by('-date')
        return render(req,'stockpred.html',{'sps':sps,'username':req.user.username})
    else:
        form = AuthenticationForm()
        return render(req,'login.html',{'form':form,'msg':'请先登录'})
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