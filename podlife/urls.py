from django.conf.urls import include, url
from podlife.views import *

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^topic/', include([
        url(r'^(?P<topic>[\w-]+)/$', TopicView.as_view()),
    ])),
    url(r'user/', include([
        url(r'^$', ListUsers.as_view(), name='list_users'),
        url(r'^(?P<username>[\w-]+)/$', UserView.as_view()),
    ])),
    url(r'^podcast/', include([
        url(r'^$', MainPage.as_view(), name='main'),
        url(r'^random/$', random, name='random'),
        url(r'^(?P<slugfield>[\w-]+)/$', PodcastView.as_view()),
    ])),
    url(r'^dashboard/', include([
        url(r'^$', Dashboard.as_view(), name='dashboard'),
        url(r'^subs/$', Subscriptions.as_view(), name="subs"),
        url(r'^stats/$', Statistics.as_view(), name='stats'),
        url(r'^manage/', include([
            url(r'^podcast/', include([
                url(r'^$', ManagePodcasts.as_view(), name='manage_podcasts'),
                url(r'^edit/(?P<slugfield>[\w-]+)/$', UpdatePodcast.as_view()),
            ])),
            url(r'^topic/$', ManageTopics.as_view(), name='manage_topics'),
            url(r'^subs/$', Subscriptions.as_view(), name="manage_subs"),  # TODO
        ])),
        url(r'^create/', include([
            url(r'^podcast/$', UploadPodcast.as_view(), name='upload_podcast'),
            url(r'^topic/$', CreateTopic.as_view(), name='create_topic'),
        ])),
        url(r'^settings/$', UserSettings.as_view(), name='settings')
    ])),
]
