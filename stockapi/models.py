# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
natures = [('exciting', 'exciting'), ('boring', 'boring')]
colors = [('red', 'red'), ('green', 'green')]


# Create your models here.
class stockData(models.Model):
	ticker = models.CharField(max_length=100, blank=False)
	open = models.FloatField()
	close = models.FloatField()
	high = models.FloatField()
	low = models.FloatField()
	date = models.BigIntegerField()
	nature = models.CharField(default='exciting', max_length=20, editable=False)
	color = models.CharField(default='red', max_length=20, editable=False)


class tickers(models.Model):
	ticker = models.CharField(max_length=20, primary_key=True)
	companyName = models.CharField(max_length=100, blank=False)