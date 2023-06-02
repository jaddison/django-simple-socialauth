from __future__ import unicode_literals
from django.urls import path

from . import views


urlpatterns = [
    path(r'^(?P<provider_type>[\w\-]+)/login/$', views.LoginView.as_view(), name='simple_socialauth-login'),
    path(r'^(?P<provider_type>[\w\-]+)/callback/$', views.CallbackView.as_view(), name='simple_socialauth-login_callback'),
    path(r'^(?P<provider_type>[\w\-]+)/complete/$', views.CompleteView.as_view(), name='simple_socialauth-login_complete'),
]
