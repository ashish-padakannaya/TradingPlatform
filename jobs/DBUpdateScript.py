#importing modules
from datetime import datetime, timedelta
import pandas as pd
import quandl
import DBUpdateConfig
from sqlalchemy import create_engine
from tqdm import tqdm
import math
import sys


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


def getIntervalLabel(row, intervalType):
    if intervalType == 'weekly':
        return str(row.Date.isocalendar()[0]) + '-' + str(row.Date.isocalendar()[1])
    if intervalType == 'monthly':
        return row.Date.strftime('%y-%m')
    if intervalType == 'quarterly':
        return row.Date.strftime('%y') + str(int(math.ceil(row.Date.month / float(3))))
    if intervalType == 'yearly':
        return row.Date.strftime('%y')


def shapeData(data, ticker, intervalType):
    data.reset_index(inplace=True)
    data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)
    data.fillna(value=0, inplace=True)

    if intervalType != 'daily':
        indexOfIntervals = {}
        orderedIntervals = []
        for index, row in data.iterrows():
            interval = getIntervalLabel(row, intervalType)
            if interval not in indexOfIntervals:
                indexOfIntervals[interval] = []
                indexOfIntervals[interval].append(index)
                orderedIntervals.append(interval)
            else:
                indexOfIntervals[interval].append(index)

        listOfDicts = []
        for intervalLabel in orderedIntervals:
            intervalRow = {'Open': None, 'Close': None, 'High': None, 'Low': 999999999999999999999, 'Date': None}
            for index, row in data.ix[indexOfIntervals[intervalLabel]].iterrows():
                if index == indexOfIntervals[intervalLabel][0]:
                    intervalRow['Open'] = row.Open
                    intervalRow['Date'] = row.Date

                if index == indexOfIntervals[intervalLabel][len(indexOfIntervals[intervalLabel]) - 1]:
                    intervalRow['Close'] = row.Close

                if row.High > intervalRow['High']:
                    intervalRow['High'] = row.High

                if row.Low < intervalRow['Low']:
                    intervalRow['Low'] = row.Low
            listOfDicts.append(intervalRow)

        data = pd.DataFrame(listOfDicts)

    else:
        dateYearAgo = datetime.now() - timedelta(days=365)
        data = data[data.Date >= dateYearAgo]

    for index, row in data.iterrows():
        nature, color = getNatureAndColor(row)
        data.set_value(index, 'color', color)
        data.set_value(index, 'nature', nature)

        pyDateTimeObj = row.Date.to_pydatetime()
        epoch = (pyDateTimeObj - datetime(1970, 1, 1)).total_seconds()
        data.set_value(index, 'Date1', epoch)

    del data['Date']
    data.rename(columns={'Date1': 'Date'}, inplace=True)

    data['ticker'] = ticker
    data = data.iloc[::-1]
    data.reset_index(inplace=True)
    del data['index']
    return data


if __name__ == '__main__':
    print 'Connect to postgres engine'
    quandl.ApiConfig.api_key = 'GX3otZafamJ5s9zfz7nR'
    engine = create_engine('postgresql://' + DBUpdateConfig.user + ':' + DBUpdateConfig.password + '@' + DBUpdateConfig.host + ':5432/' + DBUpdateConfig.database)
    print 'Connected'
    print '###################################'

    connection = engine.connect()
    #FOR INCREMENATAL POINTER CALCULATION
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
        # deleteSelective = connection.execute('delete from stockapi_tickers where ticker = \'' + ticker + '\'')
        pbar = tqdm([ticker])
    else:
        resoverall = connection.execute('select * from stockapi_tickers a, stockapi_userinterests b where a.id = b.ticker_id and b.interested = true LIMIT 10')
        tickers = pd.DataFrame(resoverall.fetchall())
        tickers.columns = resoverall.keys()
        pbar = tqdm(tickers.Code.tolist())

    stock_dataframes = []

    #fetching pointers for all tickers
    for ticker in pbar:
        pbar.set_description('Processing ' + ticker)
        try:
            rawData = quandl.get('NSE/' + ticker)
        except Exception as e:
            continue
        for interval in ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']:
            data = shapeData(rawData.copy(), ticker, interval)
            multiplier = 2
            phase2Pointers = {
                'Freshness': 0,
                'Trend': 0,
                'Gap up': 0,
                'Time Spend': 0,
                'High': 0,
                'Dividend': 0,
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

        #     print 'fetching Data for ' + ticker
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

            if interval == 'daily':
                # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                # Finding pointer 2
                # if 7th week avg<= current week avg then 1
                # $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                lastWeekFound = None
                weekAverage = {}
                for index, row in data.iterrows():
                    # gives week number of the year
                    week = datetime.fromtimestamp(row.Date).isocalendar()[1]

                    if week not in weekAverage:
                        weekAverage[week] = []
                        weekAverage[week].append(row.Close)
                    else:
                        weekAverage[week].append(row.Close)
                    lastWeekFound = week

                    # break after finding 8th week
                    if len(weekAverage.keys()) > 7:
                        break
                # print weekAverage
                if lastWeekFound is not None and len(weekAverage.keys()) > 7:
                    del weekAverage[lastWeekFound]
                    seventhWeek = weekAverage.keys()[0]
                    currentWeek = weekAverage.keys()[6]
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
            stock_dataframes.append({'ticker': ticker, 'entry': entry, 'stopLoss': stopLoss, 'target': target, 'gapUp': phase2Pointers['Gap up'], 'trend': phase2Pointers['Trend'], 'timeSpend': phase2Pointers['Time Spend'], 'high': phase2Pointers['High'], 'freshness': phase2Pointers['Freshness'], 'dividend': phase2Pointers['Dividend'], 'earning': phase2Pointers['Earning'], 'totalPoints': totalPoints, 'interval': interval})

    print 'Updating Database'
    if len(sys.argv) > 1:
        engine.execute('delete from stockapi_pointers where ticker = \'' + ticker + '\'')
    else:
        engine.execute('delete from stockapi_pointers where true')
    final_df = pd.DataFrame(stock_dataframes)
    final_df.to_sql('stockapi_pointers', engine, if_exists='append', index=False)
    print 'Update Complete. Success'
