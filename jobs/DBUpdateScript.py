#importing modules
from datetime import datetime, timedelta
import pandas as pd
import quandl
import DBUpdateConfig
import pandas as pd
from sqlalchemy import create_engine
import os
import wget
import zipfile
import time

print 'Connect to postgres engine'
quandl.ApiConfig.api_key = 'GX3otZafamJ5s9zfz7nR'
engine = create_engine('postgresql://' + DBUpdateConfig.user + ':' + DBUpdateConfig.password + '@' + DBUpdateConfig.host + ':5432/' + DBUpdateConfig.database)
print 'Connected'
print '###################################'


#fetching all ticker symbols
# print 'Checking for symbols'
# try:
#     os.remove('dataset.zip')
#     os.remove('NSE-datasets-codes.csv')
# except Exception as e:
#     print e

# wget.download("https://www.quandl.com/api/v3/databases/NSE/codes?api_key=" + quandl.ApiConfig.api_key, "dataset.zip")
# zip_ref = zipfile.ZipFile('./dataset.zip', 'r')
# zip_ref.extractall('.')
# zip_ref.close()

# data = pd.read_csv('NSE-datasets-codes.csv', header=None)
# data.rename(columns={0: 'Code', 1: 'Name'}, inplace=True)
# for index, row in data.iterrows():
#     data.set_value(index, 'Code', row.Code[4:])
# data.rename(columns={'Code': 'ticker', 'Name': 'companyName'}, inplace=True)
# data.to_sql('stockapi_tickers', engine, if_exists='replace', index=False)
# print 'Status Clean'
# print '###################################'


def getNatureAndColor(row):
	open = row.Open
	close = row.Close
	low = row.Low
	high = row.High

	body_length = 0
	stick_length = 0
	color = 'green'

	if close > open:
		color = 'green'
		body_length = close - open
	if open > close:
		color = 'red'
		body_length = open - close

	upper_stick_length = 0
	lower_stick_length = 0

	if color is 'green':
		upper_stick_length = high - close
		lower_stick_length = open - low
	else:
		upper_stick_length = high - open
		lower_stick_length = close - low

	stick_length = upper_stick_length + lower_stick_length

	if stick_length > body_length:
		nature = 'boring'
	else:
		nature = 'exciting'

	return nature, color


def shapeData(data, ticker):
    data.reset_index(inplace=True)
    data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)
    data.fillna(value=0, inplace=True)

    for index, row in data.iterrows():
        nature, color = getNatureAndColor(row)
        data.set_value(index, 'color', color)
        data.set_value(index, 'nature', nature)

    data['ticker'] = ticker
    data = data.iloc[::-1]
    data.reset_index(inplace=True)
    return data


# getting all symbols present in DB
# connection = engine.connect()
# resoverall = connection.execute('select * from stockapi_tickers')
# tickers = pd.DataFrame(resoverall.fetchall())
# tickers.columns = resoverall.keys()

# all_tickers = tickers['ticker'].tolist()
stock_dataframes = []


#fetching pointers for all tickers
for ticker in ['BHEL', 'CIPLA', 'SUNPHARMA']:
    dateYearAgo = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    data = quandl.get('NSE/' + ticker, start_date=dateYearAgo)
    data = shapeData(data, ticker)
    multiplier = 2
#     print data
    phase2Pointers = {
        'Freshness': 0,
        'Trend': 0,
        'Gap up': 0,
        'Time Spend': 0,
        'High': 0,
        'Divident': 0,
        'Earning': 0
    }

    # $$$$$$$$$$$$$$$$$$$$$
    # Finding first pointer (entry > low)
    # $$$$$$$$$$$$$$$$$$$$$
    startPoint = 0
    lowAfterEntry = None
    entryFound = False
    limitReached = False
    entryIndex = 0

    print len(data)
    while not entryFound and not limitReached and len(data) != 0:

        P1 = False
        P2 = False
        P3 = False
        P1index = None
        P2index = None
        P3index = None

        for index, row in data[startPoint:].iterrows():
            if index == len(data) - 1:
                limitReached = True

            if not P1:
                if row.color == 'green' and row.nature == 'exciting':
                    P1 = True
                    P1index = index
                    continue

            if P1 and not P2:
                if row.nature == 'boring' and index == (P1index + 1):
                    P2 = True
                    P2index = index
                    continue
                else:
                    P1 = False
                    P1index = None

            if P1 and P2 and not P3:
                if row.nature == 'exciting':
                    P3 = True
                    P3index = index
                    continue

            if P1 and P2 and P3:
                break

        # pointers found, now to find the data
        if P1 and P2 and P3:
            entry = 0
            entryAtIndex = 0
            for index, row in data[P2index:P3index].iterrows():
                if row.nature == 'boring':
                    # entry_at_index = row.High
                    entryAtIndex = max(row.Open, row.Close)
                    if entryAtIndex > entry:
                        entry = float(entryAtIndex)
                        entryIndex = index
            #finding lowest low
            for index, row in data[:entryIndex].iterrows():
                if lowAfterEntry is None or row.Low < lowAfterEntry:
                    lowAfterEntry = row.Low

            if entry > lowAfterEntry:
                startPoint = entryIndex
            else:
                entryFound = True
                stopLoss = None
                stopLossAtIndex = 0
                #stopLossIndex = 0
                for index, row in data[P1index:P3index].iterrows():
                    # if (row.color == 'green' and row.nature == 'exciting') or (row.nature == 'boring'):
                    stopLossAtIndex = row.Low
                    if stopLoss is None or stopLossAtIndex < stopLoss:
                        stopLoss = float(stopLossAtIndex)
                    # print stopLoss
                target = ((entry - stopLoss) * multiplier) + entry
                entry = round(entry, 2)
                target = round(target, 2)
                stopLoss = round(stopLoss, 2)
                phase2Pointers['Freshness'] = 1

    if not entryFound:
        entry = 0
        stopLoss = 0
        target = 0

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Finding pointer 2
    # if 7th week avg<= current week avg then 1
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    lastWeekFound = None
    weekAverage = {}
    for index, row in data.iterrows():
        # gives week number of the year
        week = row.Date.isocalendar()[1]

        if week not in weekAverage:
            weekAverage[week] = []
            weekAverage[week].append(row.Close)
        else:
            weekAverage[week].append(row.Close)
        lastWeekFound = week

        # break after finding 8th week
        if len(weekAverage.keys()) > 7:
            break

    if lastWeekFound is not None:
        del weekAverage[lastWeekFound]
        seventhWeek = lastWeekFound + 1
        currentWeek = seventhWeek + 6
    if len(weekAverage.keys()) == 7:
        seventhAverage = sum(weekAverage[seventhWeek]) / float(len(weekAverage[seventhWeek]))
        currentAverage = sum(weekAverage[currentWeek]) / float(len(weekAverage[currentWeek]))

        if seventhAverage <= currentAverage:
            phase2Pointers['Trend'] = 1

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Pointer 3 should be green
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    if entryFound:
        if data.iloc[P3index].color == 'green':
            phase2Pointers['Gap up'] += 1

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # While finding pointer 1 and 2 if the low of the excting body(open) > immidiate boring candle body high (open if it is red else close)
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    if entryFound:
        excitingBodyLow = data.iloc[P1index].Open
        colorOfNextBoringCandle = data.iloc[P1index + 1].color
        if colorOfNextBoringCandle == 'green':
            if excitingBodyLow > data.iloc[P1index + 1].Close:
                phase2Pointers['Gap up'] += 1
        else:
            if excitingBodyLow > data.iloc[P1index + 1].Open:
                phase2Pointers['Gap up'] += 1

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # number of boring candles between green excing and exciting pointer 2 and 3
    # <=3 then 2 points
    # >3 and <=6 then 1 points
    # otherwise 0
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    if entryFound:
        boringCandleCount = P3index - P1index - 1
        if boringCandleCount <= 3:
            phase2Pointers['Time Spend'] += 2
        if 3 < boringCandleCount <= 6:
            phase2Pointers['Time Spend'] += 1

    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    # Find the high before the entry
    # Entry + (Entry-stop loss)*6 >=High -> 2 points
    # Entry + (Entry-stop loss)*4 >=High -> 1 points
    # otherwise 0
    # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
    if entryFound:
        high = 0
        for index, row in data[:entryIndex].iterrows():
            if row.High > high:
                high = row.High
        if (entry + (entry - stopLoss) * 6) >= high:
            phase2Pointers['High'] += 2
        elif (entry + (entry - stopLoss) * 4) >= high:
            phase2Pointers['High'] += 1

    totalPoints = sum(phase2Pointers.values())
    data_to_return = {'ticker': ticker, 'entry': entry, 'stopLoss': stopLoss, 'target': target, 'gapUp': phase2Pointers['Gap up'], 'trend': phase2Pointers['Trend'], 'timeSpend': phase2Pointers['Time Spend'], 'high': phase2Pointers['High'], 'totalPoints': totalPoints}
    stock_dataframes.append(data_to_return)


print 'Updating Database'
final_df = pd.DataFrame(stock_dataframes)
final_df.to_sql('stockapi_pointers', engine, if_exists='replace', index=False)
print 'Update Complete. Success'