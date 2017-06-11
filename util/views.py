# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.response import Response
# from util.serializers import userSerializer
# from util.models import Profile


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


# class profileList(generics.ListCreateAPIView):
# 	queryset = Profile.objects.all()
# 	serializer_class = userSerializer


# class profileDetails(generics.RetrieveUpdateDestroyAPIView):
# 	queryset = Profile.objects.all()
# 	serializer_class = userSerializer

# 	def get(self, request, pk, format=None):
# 		user = request.user
# 		prof = Profile.objects.get(user=pk)
# 		serializer = userSerializer(prof)
# 		return Response(serializer.data)

	# def put(self, request, pk, format=None):
	# 	print pk
	# 	prof = Profile.objects.get(user_id=pk)
	# 	print request.data
	# 	requestData = request.data
	# 	requestData['user'] = prof
	# 	serializer = userSerializer(prof, data=request.data)
	# 	if serializer.is_valid():
	# 		serializer.save()
	# 		return Response(serializer.data)
	# 	return Response(serializer.errors)
