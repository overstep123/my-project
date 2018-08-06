import test_get_price
import test_feature
import test_is_Down
import classfier_test
import price_data_migration
import http.client, urllib
import os
import datetime as dt
import time
import progressbar
import pandas as pd
from sqlalchemy import create_engine
import tushare as ts

count = 0;
start_date = '2018-07-23'
bar = progressbar.ProgressBar(maxval=5000).start();
test_feature.test_feature(start_date,bar,count);
