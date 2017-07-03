# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# import time
from django.db import models
# from django.contrib.auth.models import User
from django.db.models.signals import post_save
import os


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
	Code = models.CharField(max_length=100)
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
	interval = models.CharField(max_length=20, default='daily')


class userInterests(models.Model):
	ticker = models.ForeignKey(tickers, on_delete=models.CASCADE)
	interested = models.BooleanField(default=False)

	__original_interest = None

	def __init__(self, *args, **kwargs):
		super(userInterests, self).__init__(*args, **kwargs)
		self.__original_interest = self.interested

	def save(self, force_insert=False, force_update=False, *args, **kwargs):
		if self.interested != self.__original_interest and self.interested is True:
			os.system('python jobs/DBUpdateScript.py ' + self.ticker.Code + '&')

		super(userInterests, self).save(force_insert, force_update, *args, **kwargs)
		self.__original_interest = self.interested


# Signal to create User userInterests for any ticker added by user
def generateInterests(sender, instance, **kwargs):
    if kwargs['created']:
    	userInterests(ticker=instance, interested=False).save()


post_save.connect(generateInterests, sender=tickers)
