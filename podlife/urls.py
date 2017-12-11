from django.conf.urls import include, url
from podlife.views import *

urlpatterns = [
    url(r'^$', HomePage.as_view(), name='home'),
    url(r'^topic/', include([
        url(r'^$', ListTopics.as_view(), name='list_topics'),
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
        url(r'^manage/', include([
            url(r'^podcast/', include([
                url(r'^$', ManagePodcasts.as_view(), name='manage_podcasts'),
                url(r'^(?P<slugfield>[\w-]+)/$', UpdatePodcast.as_view()),
            ])),
            url(r'^topic/$', ManageTopics.as_view(), name='manage_topics'),
            url(r'^subs/$', ManageSubscriptions.as_view(), name="manage_subs"),
        ])),
        url(r'^create/', include([
            url(r'^podcast/$', UploadPodcast.as_view(), name='upload_podcast'),
            url(r'^topic/$', CreateTopic.as_view(), name='create_topic'),
        ])),
        url(r'^settings/$', UserSettings.as_view(), name='settings')
    ])),
    url(r'^upvote/', include([
        url(r'^(?P<slugfield>[\w-]+)/$', upvote, name='upvote'),
        url(r'^(?P<slugfield>[\w-]+)/(?P<origin>[\w-]+)/$', upvote, name='upvote'),
        ])),
    url(r'^downvote/', include([
        url(r'^(?P<slugfield>[\w-]+)/$', downvote, name='downvote'),
        url(r'^(?P<slugfield>[\w-]+)/(?P<origin>[\w-]+)/$', downvote, name='downvote'),
        ])),
    url(r'^usersubscribe/(?P<creator_username>[\w-]+)/(?P<user_id>[0-9]+)/$', user_subscribe, name='user_subscribe'),
    url(r'^userunsubscribe/(?P<creator_username>[\w-]+)/(?P<user_id>[0-9]+)/$', user_unsubscribe, name='user_unsubscribe'),
    url(r'^topicsubscribe/(?P<topic>[\w-]+)/(?P<user_id>[0-9]+)/$', topic_subscribe, name='topic_subscribe'),
    url(r'^topicunsubscribe/(?P<topic>[\w-]+)/(?P<user_id>[0-9]+)/$', topic_unsubscribe, name='topic_unsubscribe'),
    url(r'^dashboarduserunsubscribe/(?P<creator_username>[\w-]+)/(?P<user_id>[0-9]+)/$', dashboard_user_unsubscribe, name='dashboard_user_unsubscribe'),
    url(r'^dashboardtopicunsubscribe/(?P<topic>[\w-]+)/(?P<user_id>[0-9]+)/$', dashboard_topic_unsubscribe, name='dashboard_topic_unsubscribe')
]
