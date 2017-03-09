from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from requests_oauthlib import OAuth1Session, OAuth2Session

from ..settings import SIMPLE_SOCIALAUTH_SITEROOT, SIMPLE_SOCIALAUTH_SECURE, SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS


class BaseProvider(object):
    type = None
    name = None

    @classmethod
    def display_name(cls):
        if cls.name:
            return cls.name
        return cls.type.title()

    def __init__(self, oauth1=False, **kwargs):
        if self.type is None:
            raise Exception('Social provider missing `type` attribute.')

        self.oauth1 = oauth1

        self.settings = SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS.get(self.type, {})
        if not self.settings:
            raise Exception('{0} social provider missing settings.'.format(self.type.title()))

        self.initialize_settings = self.settings.get('init_params', {}).copy()
        self.initialize_settings.update(kwargs)

        self.site_root = SIMPLE_SOCIALAUTH_SITEROOT
        if not self.site_root:
            self.site_root = "{0}://{1}".format('https' if SIMPLE_SOCIALAUTH_SECURE else 'http', Site.objects.get_current().domain)

        callback_uri = '{0}{1}'.format(
            self.site_root,
            reverse('simple_socialauth-login_callback', args=(self.type,))
        )

        if oauth1:
            self.session = OAuth1Session(
                callback_uri=callback_uri,
                **self.initialize_settings
            )
        else:
            self.session = OAuth2Session(
                redirect_uri=callback_uri,
                **self.initialize_settings
            )

    def connect(self, **kwargs):
        authorization_url = getattr(self, 'authorization_url', None)
        if not authorization_url:
            raise Exception(
                'no authorization_url set for provider: '.format(self.type)
            )

        self.authorize_params = self.settings.get('authorize_params', {}).copy()
        self.authorize_params.update(kwargs)

        if self.oauth1:
            request_token_url = getattr(self, 'request_token_url', None)
            if not request_token_url:
                raise Exception(
                    'no request_token_url set for provider: '.format(self.type)
                )

            self.session.fetch_request_token(
                request_token_url,
                **self.authorize_params
            )
            return self.session.authorization_url(authorization_url)
        else:
            url, state = self.session.authorization_url(
                authorization_url,
                **self.authorize_params
            )
            return url

    def callback(self, oauth_data, **kwargs):
        access_token_url = getattr(self, 'access_token_url', None)
        if not access_token_url:
            raise Exception(
                'no access_token_url set for provider: '.format(self.type)
            )

        self.callback_params = self.settings.get('callback_params', {}).copy()
        self.callback_params.update(kwargs)

        if self.oauth1:
            self.session.parse_authorization_response(oauth_data)
            return self.session.fetch_access_token(
                access_token_url,
                **self.callback_params
            )
        else:
            return self.session.fetch_token(
                access_token_url,
                authorization_response=oauth_data,
                **self.callback_params
            )

    def get_social_user_info(self):
        return {}


