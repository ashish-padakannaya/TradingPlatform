from django.conf.urls import url
from stockapi import views

urlpatterns = [
    url(r'^stock/$', views.getStock.as_view()),
    url(r'^getPopularTickers/$', views.getPopularTickers.as_view()),
    url(r'^userInterests/$', views.userInterestList.as_view()),
    url(r'^tickers/$', views.tickers.as_view()),
    url(r'^pointers/$', views.allPointers.as_view()),
    url(r'^pointers2/$', views.getPointer.as_view())
]
