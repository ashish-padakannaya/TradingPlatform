# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import time
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# Create your models here.
class stockData(models.Model):
	ticker = models.CharField(max_length=100, blank=False)
	open = models.FloatField()
	close = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	date = models.BigIntegerField(default=1)
	nature = models.CharField(default='exciting', max_length=20, editable=False)
	color = models.CharField(default='red', max_length=20, editable=False)


class tickers(models.Model):
	Code = models.CharField(max_length=20)
	Name = models.CharField(max_length=100, blank=False)


class pointers(models.Model):
	ticker = models.CharField(max_length=20)
	entry = models.FloatField()
	stopLoss = models.FloatField()
	target = models.FloatField()
	gapUp = models.IntegerField(default=0)
	trend = models.IntegerField(default=0)
	timeSpend = models.IntegerField(default=0)
	high = models.IntegerField(default=0)
	totalPoints = models.IntegerField(default=0)
	freshness = models.IntegerField(default=0)
	dividend = models.IntegerField(default=0)
	earning = models.IntegerField(default=0)



class userInterests(models.Model):
	ticker = models.ForeignKey(tickers, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	interested = models.BooleanField(default=False)


# Signal to create User userInterests
def generateInterestsForUser(sender, instance, **kwargs):
    if kwargs['created']:
    	for ticker in tickers.objects.all():
    		userInterests(ticker=ticker, user=instance, interested=True).save()


post_save.connect(generateInterestsForUser, sender=User)
