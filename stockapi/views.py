# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from rest_framework import generics, status
#from stockapi.models import stockData
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta
import pandas as pd
import zipfile
import wget
import os


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


#create User programmatically
class createUser(generics.ListCreateAPIView):
	authentication_classes = []
	permission_classes = []

	def post(self, request, format=None):
		try:
			username = str(request.data['username'])
			email = str(request.data['email'])
			password = str(request.data['password'])
			user = User.objects.create_user(username, email, password)
		except Exception as e:
			return Response(e.message, status=status.HTTP_400_BAD_REQUEST)
		user.save()

		return Response('success')


class getAllStocks(generics.ListCreateAPIView):
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


class getStock(APIView):
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


class getPointer(APIView):
	def post(self, request, format=None):
		print request.data
		multiplier = 2
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

		P1 = False
		P2 = False
		P3 = False
		P1index = None
		P2index = None
		P3index = None

		for index, row in data.iterrows():
			nature, color = getNatureAndColor(row)

			# if lowAfterEntry is None or row.Low < lowAfterEntry:
			# 	lowAfterEntry = row.Low

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

			if P1 and P2 and P3:
				break

		if not P1 and not P2 and not P3:
			return Response({'entry': None, 'stopLoss': None, 'target': None})

		# if index == len(data) - 1:
		# 	endOfDataHit = True

		# print P1index
		# print data.loc[[P1index]]
		# print P2index
		# print data.loc[[P2index]]
		# print P3index
		# print data.loc[[P3index]]
		# print 'pointers found'

		# pointers found, now to find the data
		entry = 0
		entry_at_index = 0
		for index, row in data[P2index:P3index].iterrows():
			if row.nature == 'boring':
				# entry_at_index = row.High
				entry_at_index = max(row.Open, row.Close)
				if entry_at_index > entry:
					entry = float(entry_at_index)

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

		data_to_return = {'entry': entry, 'stopLoss': stopLoss, 'target': target}

		return Response(data_to_return)
