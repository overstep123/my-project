import price_data_migration
import progressbar
import test

start_date='2015-01-13'
price_num = 5000
feature_num = 5000
down_num = 5000
train_times = 1200
count=0

bar = progressbar.ProgressBar(maxval=price_num+feature_num+down_num+1+train_times).start()
price_data_migration.get_price(start_date,bar,count)


