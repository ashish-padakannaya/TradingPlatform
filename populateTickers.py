from stockapi.models import tickers, userInterests
import quandl
import pandas as pd
import wget
import os
import zipfile
# quandl.ApiConfig.api_key = 'VHeUNLxuAngRYDgtjD9X'
quandl.ApiConfig.api_key = 'GX3otZafamJ5s9zfz7nR'


try:
    os.remove('dataset.zip')
    os.remove('NSE-datasets-codes.csv')
except Exception as e:
	print e

wget.download("https://www.quandl.com/api/v3/databases/NSE/codes?api_key=" + quandl.ApiConfig.api_key, "dataset.zip")
zip_ref = zipfile.ZipFile('./dataset.zip', 'r')
zip_ref.extractall('.')
zip_ref.close()

data = pd.read_csv('NSE-datasets-codes.csv', header=None)
data.rename(columns={0: 'Code', 1: 'Name'}, inplace=True)
for index, row in data.iterrows():
    data.set_value(index, 'Code', row.Code[4:])

for index, row in data.iterrows():
	tickers(Code=row.Code, Name=row.Name).save()

popularTickers = pd.read_csv('ind_nifty200list.csv')
popularTickers = popularTickers['Symbol'].tolist()

popularTickerIds = list(tickers.objects.filter(Code__in=popularTickers).values_list('id', flat=True))
userInterests.objects.filter(ticker__in=popularTickerIds).update(interested=True)
