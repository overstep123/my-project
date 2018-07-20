import price_data_migration
import progressbar

start_date='2018-05-25' 
price_num = 5000
feature_num = 5000
down_num = 5000
train_times = 1200
count=0
# with progressbar.ProgressBar(max_value=price_num+feature_num+down_num+1,redirect_stdout=True) as bar:
bar = progressbar.ProgressBar(maxval=price_num+feature_num+down_num+1+train_times).start()
price_data_migration.get_price(start_date,bar,count)
