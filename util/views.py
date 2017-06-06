# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response


# Create your views here.
class checkIfEmailExists(generics.ListCreateAPIView):
	authentication_classes = []
	permission_classes = []

	def get(self, request, format=None):
		email = request.GET.get('email')
		try:
			user = User.objects.get(email=email)

		except Exception as ex:
			exceptionType = type(ex).__name__
			if exceptionType == 'DoesNotExist':
				return Response(True)
		return Response(False)
