from django.contrib.auth import views as auth_views
from django.conf.urls import include, url

from podlife.views import *

urlpatterns = [
  url(r'^$', HomePage.as_view(), name='home'),
  url(r'^list/$', PodcastList.as_view(), name='list'),
  url(r'^random/$', random, name='random'),
  url(r'^podcast/(?P<slugfield>[\w-]+)/', PodcastView.as_view()),
  url(r'^dashboard/', include([
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^stats/$', Statistics.as_view(), name='stats'),
    url(r'^manage/', include ([
      url(r'^$', PodcastManage.as_view(), name='manage'),
      url(r'^(?P<slugfield>[\w-]+)/', PodcastUpdate.as_view()),
    ])),
    url(r'^create/$', PodcastCreate.as_view(), name='create'),
    url(r'^settings/', UserSettings.as_view(), name='settings')
  ])),
]
