from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required

from podlife.views import *

urlpatterns = [
  url(r'^$', HomePage.as_view(), name='home'),
  url(r'^list/$', PodcastListView.as_view(), name='list'),
  url(r'^profile/$', Profile.as_view(), name='profile'),
  url(r'^stats/$', Statistics.as_view(), name='stats'),
  url(r'^create/$', PodcastsCreate.as_view(), name='create'),
  url(r'^podcast/(?P<slugfield>[\w-]+)/', include([
    url(r'^$', PodcastView.as_view()),
    url(r'^edit/$', PodcastsUpdate.as_view()),
  ])),
]
