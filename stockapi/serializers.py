from stockapi.models import stockData, tickers, pointers, userInterests
from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin


class stockDataSerilaizer(serializers.ModelSerializer):
    class Meta:
        model = stockData
        fields = ('id', 'ticker', 'open', 'close', 'high', 'low', 'date', 'nature', 'color')


class tickerSerializer(serializers.ModelSerializer):
	class Meta:
		model = tickers
		fields = ('id', 'Code', 'Name')


class pointerSerializer(serializers.ModelSerializer):
    class Meta:
        model = pointers
        fields = ('id', 'ticker', 'entry', 'stopLoss', 'target', 'gapUp', 'trend', 'high', 'timeSpend', 'totalPoints')


# class userInterestSerializer(serializers.ModelSerializer):
#     ticker_details = tickerSerializer(source='ticker', read_only=True)
#     # pointer_details = pointerSerializer(source='pointer', read_only=True)

#     class Meta:
#         model = userInterests
#         fields = ('id', 'ticker', 'user', 'interested', 'ticker_details')


class userInterestSerializer(BulkSerializerMixin, serializers.ModelSerializer):
    ticker_details = tickerSerializer(source='ticker', read_only=True)
    # pointer_details = pointerSerializer(source='pointer', read_only=True)

    class Meta:
        model = userInterests
        fields = ('id', 'ticker', 'user', 'interested', 'ticker_details')
        list_serializer_class = BulkListSerializer
