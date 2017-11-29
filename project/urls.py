from django.contrib.auth import views as auth_views
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from project.views import *

urlpatterns = [
  url(r'^admin/', admin.site.urls),
  url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
  url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
  url(r'^password_change/$', auth_views.PasswordChangeView.as_view(), name='password_change'),
  url(r'^password_change_done/$', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
  url(r'^signup/$', Signup.as_view(), name='signup'),
  url(r'^', include('podlife.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)