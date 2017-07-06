# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from django.contrib.auth.models import User
from rest_framework import generics, status
from stockapi.models import userInterests, tickers, pointers
from stockapi.serializers import userInterestSerializer, tickerSerializer, pointerSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_tracking.models import APIRequestLog
from rest_framework_bulk import ListBulkCreateUpdateDestroyAPIView
import ast
import quandl
import math
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath('./jobs'))
print sys.path

from DBUpdateScript import getNatureAndColor, getIntervalLabel, shapeData

# quandl.ApiConfig.api_key = 'VHeUNLxuAngRYDgtjD9X'
quandl.ApiConfig.api_key = 'GX3otZafamJ5s9zfz7nR'


# def getNatureAndColor(row):
#     open = row.Open
#     close = row.Close
#     low = row.Low
#     high = row.High

#     body_length = 0
#     stick_length = 0
#     color = 'green'

#     if close > open:
#         color = 'green'
#         body_length = close - open
#     if open > close:
#         color = 'red'
#         body_length = open - close

#     upper_stick_length = 0
#     lower_stick_length = 0

#     if color is 'green':
#         upper_stick_length = high - close
#         lower_stick_length = open - low
#     else:
#         upper_stick_length = high - open
#         lower_stick_length = close - low

#     stick_length = upper_stick_length + lower_stick_length

#     if stick_length > body_length:
#         nature = 'boring'
#     else:
#         nature = 'exciting'

#     return nature, color


# def getIntervalLabel(row, intervalType):
#     if intervalType == 'weekly':
#         return str(row.Date.isocalendar()[0]) + '-' + str(row.Date.isocalendar()[1])
#     if intervalType == 'monthly':
#         return row.Date.strftime('%y-%m')
#     if intervalType == 'quarterly':
#         return row.Date.strftime('%y') + str(int(math.ceil(row.Date.month / float(3))))
#     if intervalType == 'yearly':
#         return row.Date.strftime('%y')


# def shapeData(data, ticker, intervalType=None):
#     data.reset_index(inplace=True)
#     data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)
#     data.fillna(value=0, inplace=True)
#     indexOfIntervals = {}
#     orderedIntervals = []
#     if intervalType != 'daily':
#         for index, row in data.iterrows():
#             interval = getIntervalLabel(row, intervalType)
#             if interval not in indexOfIntervals:
#                 indexOfIntervals[interval] = []
#                 indexOfIntervals[interval].append(index)
#                 orderedIntervals.append(interval)
#             else:
#                 indexOfIntervals[interval].append(index)

#         listOfDicts = []
#         for intervalLabel in orderedIntervals:
#             intervalRow = {'Open': None, 'Close': None, 'High': None, 'Low': 999999999999999999999, 'Date': None}
#             for index, row in data.ix[indexOfIntervals[intervalLabel]].iterrows():
#                 if index == indexOfIntervals[intervalLabel][0]:
#                     intervalRow['Open'] = row.Open
#                     intervalRow['Date'] = row.Date

#                 if index == indexOfIntervals[intervalLabel][len(indexOfIntervals[intervalLabel]) - 1]:
#                     intervalRow['Close'] = row.Close

#                 if row.High > intervalRow['High']:
#                     intervalRow['High'] = row.High

#                 if row.Low < intervalRow['Low']:
#                     intervalRow['Low'] = row.Low
#             listOfDicts.append(intervalRow)

#         data = pd.DataFrame(listOfDicts)

#     for index, row in data.iterrows():
#         nature, color = getNatureAndColor(row)
#         data.set_value(index, 'color', color)
#         data.set_value(index, 'nature', nature)

#         pyDateTimeObj = row.Date.to_pydatetime()
#         epoch = (pyDateTimeObj - datetime(1970, 1, 1)).total_seconds()
#         data.set_value(index, 'Date1', epoch)

#     del data['Date']
#     data.rename(columns={'Date1': 'Date'}, inplace=True)
#     data['ticker'] = ticker
#     data = data.iloc[::-1]
#     data.reset_index(inplace=True)
#     del data['index']
#     return data


#get popular tickers for a user
class getPopularTickers(LoggingMixin, generics.ListCreateAPIView):
	def get(self, request, format=None):
		history = APIRequestLog.objects.all().filter(user=request.user.id, path='/pointers/', status_code=200)
		tickerCount = {}
		for item in history:
			ticker = ast.literal_eval(item.__dict__['data'])['ticker']
			if ticker not in tickerCount:
				tickerCount[ticker] = 1
			else:
				tickerCount[ticker] += 1
		return Response(tickerCount)


class getStock(LoggingMixin, APIView):
	def post(self, request, format=None):
		print request.data
		ticker = request.data['ticker']
		interval = request.data['interval']
		start_date = datetime.strftime(datetime.now() - timedelta(days=365), '%Y-%m-%d')
		end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
		if 'start_date' in request.data:
			start_date = request.data['start_date']
		if 'end_date' in request.data:
			end_date = request.data['end_date']

		table_code = 'NSE/' + ticker

		try:
			print interval
			if interval != 'daily':
				print 'whaaa'
				data = quandl.get(table_code)
			else:
				data = quandl.get(table_code, start_date=start_date, end_date=end_date)
		except Exception:
			return Response('Incorrect ticker', status=status.HTTP_400_BAD_REQUEST)

		data = shapeData(data, ticker, interval)

		data = data.T.to_dict().values()

		return Response(data)


class tickers(LoggingMixin, generics.ListCreateAPIView):
	queryset = tickers.objects.all()
	serializer_class = tickerSerializer


class allPointers(LoggingMixin, generics.ListAPIView):
	queryset = pointers.objects.all()
	serializer_class = pointerSerializer

	def get(self, request, format=None):
		if 'interval' not in request.GET:
			return Response('Please pass interval in query parameter', status=status.HTTP_400_BAD_REQUEST)
		interval = request.GET['interval']
		try:
		    ticker = request.GET['ticker']
		    if not pointers.objects.filter(ticker=ticker, interval=interval).exists():
		    	os.system('python jobs/DBUpdateScript.py ' + ticker)
		    pointer = pointers.objects.get(ticker=ticker, interval=interval)
		    return Response(pointerSerializer(pointer).data)
		except Exception as e:
			print e
			interestObjects = userInterests.objects.filter(interested=True)
			interestedTickers = []
			for interest in interestObjects:
				interestedTickers.append(interest.ticker.Code)

			interestedPointers = pointers.objects.filter(ticker__in=interestedTickers, interval=interval)
			return Response(pointerSerializer(interestedPointers, many=True).data)


class userInterestList(LoggingMixin, ListBulkCreateUpdateDestroyAPIView):
	queryset = userInterests.objects.all()
	serializer_class = userInterestSerializer
