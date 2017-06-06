# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from django.contrib.auth.models import User
from rest_framework import generics, status
#from stockapi.models import stockData
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
import pandas as pd
import zipfile
import wget
import os
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_tracking.models import APIRequestLog
import ast

import quandl
# quandl.ApiConfig.api_key = 'VHeUNLxuAngRYDgtjD9X'
quandl.ApiConfig.api_key = 'GX3otZafamJ5s9zfz7nR'


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


#get popular tickers for a user
class getPopularTickers(generics.ListCreateAPIView):
	def get(self, request, format=None):
		history = APIRequestLog.objects.all().filter(user=request.user, path='/pointers/', status_code=200)
		tickerCount = {}
		for item in history:
			ticker = ast.literal_eval(item.__dict__['data'])['ticker']
			if ticker not in tickerCount:
				tickerCount[ticker] = 1
			else:
				tickerCount[ticker] += 1
		return Response(tickerCount)


class getAllStocks(LoggingMixin, generics.ListCreateAPIView):
	# queryset = stockData.objects.all()
	# serializer_class = stockSerializer
	def get(self, request, format=None):
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

		return Response(data.T.to_dict().values())


class getStock(LoggingMixin, APIView):
	def post(self, request, format=None):
		print request.data
		ticker = request.data['ticker']
		# start_date = datetime.strftime(datetime.now() - timedelta(days=365), '%Y-%m-%d')
		# end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
		start_date = None
		end_date = None
		if 'start_date' in request.data:
			start_date = request.data['start_date']
		if 'end_date' in request.data:
			end_date = request.data['end_date']

		table_code = 'NSE/' + ticker

		try:
			if start_date is not None and end_date is not None:
				data = quandl.get(table_code, start_date=start_date, end_date=end_date)
			else:
				data = quandl.get(table_code)
		except Exception:
			return Response('Incorrect ticker', status=status.HTTP_400_BAD_REQUEST)

		data.reset_index(inplace=True)
		data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)
		data.fillna(value=0, inplace=True)

		# setting nature and color of the stock data
		for index, row in data.iterrows():
			nature, color = getNatureAndColor(row)
			data.set_value(index, 'color', color)
			data.set_value(index, 'nature', nature)

		data = data.T.to_dict().values()

		return Response(data)


class getPointer(LoggingMixin, APIView):
	def post(self, request, format=None):
		multiplier = 3
		if 'multiplier' in request.data:
			multiplier = float(request.data['multiplier'])
		if 'ticker' in request.data:
			ticker = request.data['ticker']
		else:
			return Response('no ticker found', status=status.HTTP_400_BAD_REQUEST)

		table_code = 'NSE/' + ticker
		try:
			startDate = datetime.strftime(datetime.now() - timedelta(days=365), '%Y-%m-%d')
			endDate = datetime.strftime(datetime.now(), '%Y-%m-%d')
			data = quandl.get(table_code, start_date=startDate, end_date=endDate)
		except Exception:
			return Response('Incorrect ticker', status=status.HTTP_400_BAD_REQUEST)

		data.reset_index(inplace=True)
		data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)
		data = data.iloc[::-1]
		data.reset_index(inplace=True)

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
				nature, color = getNatureAndColor(row)

				data.set_value(index, 'color', color)
				data.set_value(index, 'nature', nature)

				if not P1:
					if color == 'green' and nature == 'exciting':
						P1 = True
						P1index = index
						continue

				if P1 and not P2:
					if nature == 'boring' and index == (P1index + 1):
						P2 = True
						P2index = index
						continue
					else:
						P1 = False
						P1index = None

				if P1 and P2 and not P3:
					if nature == 'exciting':
						P3 = True
						P3index = index
						continue

				if index == len(data) - 1:
					limitReached = True

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
					print '$$$$'
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
					phase2Pointers['Freshness'] = 1

		if not entryFound:
			entry = None
			stopLoss = None
			target = None
		# data.to_csv('head.csv', index=False)

		# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
		# Finding pointer 2
		# if 7th week avg<= current week avg then 1
		# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
		lastWeekFound = None
		weekAverage = {}
		for index, row in data.iterrows():
			week = row.Date.isocalendar()[1]
			if week not in weekAverage:
				weekAverage[week] = []
				weekAverage[week].append(row.Close)
			else:
				weekAverage[week].append(row.Close)
			lastWeekFound = week
			if len(weekAverage.keys()) > 7:
				break
		if lastWeekFound is not None:
			del weekAverage[lastWeekFound]
		if len(weekAverage.keys()) == 7:
			averages = []
			for week in weekAverage.keys():
				closeList = weekAverage[week]
				averages.append(sum(closeList) / float(len(closeList)))
			if(averages[6] <= averages[0]):
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
		# Entry + (Entry-stop loss)*6 >=High -> 2 poits
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
		data_to_return = {'entry': entry, 'stopLoss': stopLoss, 'target': target, 'pointers': phase2Pointers, 'totalPoints': totalPoints}
		return Response(data_to_return)
