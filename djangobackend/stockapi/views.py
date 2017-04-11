# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import generics, status
from stockapi.models import stockData
from stockapi.serializers import stockSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime, timedelta

import quandl
quandl.ApiConfig.api_key = 'VHeUNLxuAngRYDgtjD9X'


# Create your views here.
class getAllStocks(generics.ListCreateAPIView):
	queryset = stockData.objects.all()
	serializer_class = stockSerializer


class getStock(APIView):
	def post(self, request, format=None):
		print request.data
		ticker = request.data['ticker']
		start_date = datetime.strftime(datetime.now() - timedelta(days=365), '%Y-%m-%d')
		end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
		end_date = None
		if 'start_date' in request.data:
			start_date = request.data['start_date']
		if 'end_date' in request.data:
			end_date = request.data['end_date']

		table_code = 'NSE/' + ticker

		try:
			data = quandl.get(table_code, start_date=start_date, end_date=end_date)
		except Exception:
			return Response('Incorrect ticker', status=status.HTTP_400_BAD_REQUEST)

		data.reset_index(inplace=True)
		data.drop(['Last', 'Total Trade Quantity', 'Turnover (Lacs)'], axis=1, inplace=True)

		# setting nature and color of the stock data
		for index, row in data.iterrows():
			open = row.Open
			close = row.Close
			low = row.Low
			high = row.High

			if close > open:
				color = 'green'
			else:
				color = 'red'

			stick_length = close - open

			upper_shadow_length = 0
			lower_shadow_lenght = 0

			if high > close:
				upper_shadow_length = high - close
			if low < open:
				lower_shadow_lenght = open - low

			shadow_length = upper_shadow_length + lower_shadow_lenght

			if shadow_length >= stick_length:
				nature = 'exciting'
			else:
				nature = 'boring'

			data.set_value(index, 'color', color)
			data.set_value(index, 'nature', nature)

		data = data.T.to_dict().values()

		return Response(data)


class getPointer(APIView):
	def post(self, request, format=None):
		print request.data
		if 'ticker' in request.data:
			ticker = request.data['ticker']
		else:
			return Response('no ticker found', status=status.HTTP_400_BAD_REQUEST)

		table_code = 'NSE/' + ticker
		try:
			data = quandl.get(table_code)
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
			open = row.Open
			close = row.Close
			low = row.Low
			high = row.High

			if close > open:
				color = 'green'
			else:
				color = 'red'

			stick_length = close - open

			upper_shadow_length = 0
			lower_shadow_lenght = 0

			if high > close:
				upper_shadow_length = high - close
			if low < open:
				lower_shadow_lenght = open - low

			shadow_length = upper_shadow_length + lower_shadow_lenght

			if shadow_length >= stick_length:
				nature = 'exciting'
			else:
				nature = 'boring'

			data.set_value(index, 'color', color)
			data.set_value(index, 'nature', nature)

			if not P1:
				if color == 'green' and nature == 'exciting':
					P1 = True
					P1index = index
					continue

			if P1 and not P2:
				if nature == 'boring':
					P2 = True
					P2index = index
					continue

			if P1 and P2 and not P3:
				if nature == 'exciting':
					P3 = True
					P3index = index
					continue

			if P1 and P2 and P3:
				break

		print P1index
		print P2index
		print P3index
		print 'sasa'

		# pointers found, now to find the data
		entry = 0
		entry_at_index = 0
		for index, row in data[P2index:P3index + 1].iterrows():
			if row.nature == 'boring':
				print row.Open
				print row.Close
				entry_at_index = max(row.Open, row.Close)
				if entry_at_index > entry:
					entry = entry_at_index

		print entry

		stopLoss = None
		stopLoss_at_index = 0
		for index, row in data[P1index:P3index].iterrows():
			if row.color == 'green':
				stopLoss_at_index = min(row.Low, row.Open, row.Close, row.High)
				if stopLoss is None or stopLoss_at_index < stopLoss:
					stopLoss = float(stopLoss_at_index)

		print stopLoss

		target = (entry - stopLoss) * 2

		data_to_return = {'entry': entry, 'stopLoss': stopLoss, 'target': target}

		return Response(data_to_return)

