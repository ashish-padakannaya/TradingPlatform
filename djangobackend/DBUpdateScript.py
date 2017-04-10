#importing necessary modules
from datetime import datetime, timedelta
import pandas as pd
import MySQLdb
import quandl
import DBUpdateConfig


#connecting to Database
conn = MySQLdb.connect(DBUpdateConfig.host, DBUpdateConfig.user, DBUpdateConfig.password, DBUpdateConfig.database)
cur = conn.cursor()

#fetching historical for missing data
cur.execute('select distinct(ticker) from stockapi_stockdata')
tickers_present = []
for row in cur.fetchall():
	tickers_present.append(row[0])
tickers_missing = [ticker for ticker in DBUpdateConfig.tickers if ticker not in tickers_present]

quandl.ApiConfig.api_key = 'VHeUNLxuAngRYDgtjD9X'

if len(tickers_missing) != 0:
	#fetching and shaping data
	print 'fetching Data for ' + ','.join(tickers_missing)
	data = quandl.get_table(DBUpdateConfig.data_table, ticker=tickers_missing, date={'gte': DBUpdateConfig.start_date, 'lte': datetime.strftime(datetime.now() - timedelta(days=1), '%Y-%m-%d')}, qopts={'columns': ['ticker', 'date', 'open', 'high', 'low', 'close']})
	data.reset_index(inplace=True)
	del data['None']

	#changing time series
	time_series = pd.to_datetime(pd.Series(data['date'].astype(str).tolist()))
	time_series = [item.strftime('%Y-%m-%d %H:%M:%S') for item in time_series]
	data.date = time_series

	dicts = data.T.to_dict().values()
	cur.executemany('insert into stockapi_stockdata(close, date, high, low, open, ticker) values (%(close)s, %(date)s, %(high)s, %(low)s, %(open)s, %(ticker)s)', dicts)


#fetching data for current date and pushing to DB
print 'fetching today\'s data'
data = quandl.get_table(DBUpdateConfig.data_table, ticker=DBUpdateConfig.tickers, date=datetime.strftime(datetime.now(), '%Y-%m-%d'), qopts={'columns': ['ticker', 'date', 'open', 'high', 'low', 'close']})
data.reset_index(inplace=True)
del data['None']

#changing time series
time_series = pd.to_datetime(pd.Series(data['date'].astype(str).tolist()))
time_series = [item.strftime('%Y-%m-%d %H:%M:%S') for item in time_series]
data.date = time_series

dicts = data.T.to_dict().values()
cur.executemany('insert into stockapi_stockdata(close, date, high, low, open, ticker) values (%(close)s, %(date)s, %(high)s, %(low)s, %(open)s, %(ticker)s)', dicts)

cur.close()
conn.commit()
