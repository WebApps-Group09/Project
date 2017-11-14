from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views

from podlife.views import *

urlpatterns = [
	url(r'^$', PodcastListView.as_view(), name='home'),
	url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
	url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
	url(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
	url(r'^password_change_done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
	url(r'^signup/$', Signup.as_view(), name='signup'),
	url(r'^profile/$', Profile.as_view(), name='profile'),
	url(r'^create/$', PodcastsCreate.as_view(), name='create'),
	url(r'^podcast/(?P<slugfield>[\w-]+)/', include([
        url(r'^$', PodcastView.as_view()),
        url(r'^edit/$', PodcastsUpdate.as_view()),
    ])),
]
