from django.contrib.auth import views as auth_views
from django.conf.urls import include, url

from podlife.views import *

urlpatterns = [
  url(r'^$', HomePage.as_view(), name='home'),
  url(r'^control/', include([
    url(r'^topic/', include ([
      url(r'^$', ManageTopics.as_view(), name='manage_topics'),
      url(r'^create/$', CreateTopic.as_view(), name='create_topic'),
    ])),
  ])),
  url(r'^list/$', PodcastList.as_view(), name='list'),
  url(r'^random/$', random, name='random'),
  url(r'^podcast/(?P<slugfield>[\w-]+)/', PodcastView.as_view()),
  url(r'^dashboard/', include([
    url(r'^$', Dashboard.as_view(), name='dashboard'),
    url(r'^subs/$', Subscriptions.as_view(), name="subs"),
    url(r'^stats/$', Statistics.as_view(), name='stats'),
    url(r'^manage/', include ([
      url(r'^$', PodcastManage.as_view(), name='manage_podcasts'),
      url(r'^(?P<slugfield>[\w-]+)/', PodcastUpdate.as_view()),
	  url(r'^(?P<slugfield>[\w-]+)/', PodcastDelete.as_view()),
    ])),
    url(r'^upload/$', PodcastUpload.as_view(), name='upload_podcast'),
    url(r'^settings/$', UserSettings.as_view(), name='settings')
  ])),
]
