from stockapi.models import stockData
from rest_framework import serializers


class stockSerializer(serializers.ModelSerializer):
    class Meta:
        model = stockData
        fields = ('id', 'ticker', 'open', 'close', 'high', 'low', 'date', 'nature', 'color')
