from django.conf.urls import url
from util import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^checkEmail/$', views.checkIfEmailExists.as_view()),
    url(r'^profile/$', views.profileList.as_view()),
    url(r'^profile/(?P<pk>[0-9]+)/$', views.profileDetails.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
