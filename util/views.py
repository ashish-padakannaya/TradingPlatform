# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
from util.serializers import userSerializer
from util.models import Profile
from django.http import JsonResponse

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
				return Response(False)
		return Response(True)


class proflieList(generics.ListCreateAPIView):
	queryset = Profile.objects.all()
	serializer_class = userSerializer


class profileDetails(generics.RetrieveUpdateDestroyAPIView):
	queryset = Profile.objects.all()
	serializer_class = userSerializer

	# def get(self, request, pk):
	# 	user = request.user
	# 	serializer = userSerializer(Profile.objects.get(user=user))
	# 	return Response(serializer.data)
