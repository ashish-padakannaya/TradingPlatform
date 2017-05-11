from django.conf.urls import url
from stockapi import views

urlpatterns = [
    url(r'^stocks/$', views.getAllStocks.as_view()),
    url(r'^stock/$', views.getStock.as_view()),
    url(r'^pointers/$', views.getPointer.as_view()),
    url(r'^createUser/$', views.createUser.as_view())
]