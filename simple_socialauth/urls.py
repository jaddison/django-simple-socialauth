from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<provider_type>[\w\-]+)/login/$', views.LoginView.as_view(), name='simple_socialauth-login'),
    url(r'^(?P<provider_type>[\w\-]+)/callback/$', views.CallbackView.as_view(), name='simple_socialauth-login_callback'),
    url(r'^(?P<provider_type>[\w\-]+)/complete/$', views.CompleteView.as_view(), name='simple_socialauth-login_complete'),
]
