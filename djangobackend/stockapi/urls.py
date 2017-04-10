from django.conf.urls import url
from stockapi import views
from rest_framework.urlpatterns import format_suffix_patterns


urlpatterns = [
    url(r'^stocks/$', views.getAllStocks.as_view()),
    url(r'^stock/$', views.getStock.as_view()),
    url(r'^pointers/$', views.getPointer.as_view())
]