from __future__ import unicode_literals
from django.urls import re_path

from . import views


urlpatterns = [
    re_path(r'^(?P<provider_type>[\w\-]+)/login/$', views.LoginView.as_view(), name='simple_socialauth-login'),
    re_path(r'^(?P<provider_type>[\w\-]+)/callback/$', views.CallbackView.as_view(), name='simple_socialauth-login_callback'),
    re_path(r'^(?P<provider_type>[\w\-]+)/complete/$', views.CompleteView.as_view(), name='simple_socialauth-login_complete'),
]
