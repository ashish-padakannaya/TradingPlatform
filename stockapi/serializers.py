from stockapi.models import stockData, ticker
from rest_framework import serializers


class stockDataSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = stockData
        fields = ('id', 'ticker', 'open', 'close', 'high', 'low', 'nature', 'color')


class tickerSerializer(serializers.ModelSerializer):
	class Meta:
		model = ticker
		fields = ('ticker', 'companyName')
