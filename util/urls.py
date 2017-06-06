from django.conf.urls import url
from util import views

urlpatterns = [
    url(r'^checkEmail/$', views.checkIfEmailExists.as_view())
]
