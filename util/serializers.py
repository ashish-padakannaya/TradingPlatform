from util.models import Profile
from rest_framework import serializers


class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('user', 'bio', 'location')
