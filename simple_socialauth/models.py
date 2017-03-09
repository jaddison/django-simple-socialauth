from __future__ import unicode_literals
import datetime
import json

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible

from .providers import registry


@python_2_unicode_compatible
class SocialAccount(models.Model):
    # TODO: Does all the token related data need to move to a separate
    # 'SocialToken' model to allow for 1:many relationship with
    # SocialAccount (multiple logins/devices, etc)?

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='social_accounts', on_delete=models.CASCADE)
    provider = models.CharField(max_length=32)
    uid = models.CharField(max_length=256)

    access_token = models.TextField(default='', blank=True)
    secret = models.TextField(default='', blank=True)  # OAuth1 only
    expires = models.DateTimeField(null=True, blank=True)

    _data = models.TextField(blank=True, default="{}", help_text="Original token response from the OAuth provider.")

    class Meta:
        unique_together = ('uid', 'provider')

    def __str__(self):
        return "{}: {}".format(self.provider, self.uid)

    @property
    def data(self):
        if not hasattr(self, '_data_loaded'):
            self._data_loaded = json.loads(self._data)
        return self._data_loaded

    @data.setter
    def data(self, value):
        self._data_loaded = value
        self._data = json.dumps(value)

    @property
    def session(self):
        if not hasattr(self, '_provider'):
            if self.secret:
                # OAuth1-based
                kw = {
                    'resource_owner_key': self.access_token,
                    'resource_owner_secret': self.secret
                }
            else:
                # OAuth2-based
                if self.data:
                    # NOTE: auto-refreshing the URL ought to just 'work'
                    # if all the arguments are passed in properly during
                    # initialization
                    kw = {'token': self.data}
                else:
                    kw = {
                        'token': {
                            'token_type': 'Bearer',
                            'access_token': self.access_token
                        }
                    }
            self._provider = registry.get(self.provider, **kw)

        return self._provider.session

    @classmethod
    def create_or_update(cls, user, user_info, token_data):
        uid = user_info.get('uid')
        provider = user_info.get('provider')

        # OAUTH2: if expires_in is in the token data
        expires_in = token_data.get('expires_in')
        # OAUTH1: if secret is set in the token data
        secret = token_data.get('oauth_token_secret', '')

        access_token = token_data.get('access_token', '')
        if secret:
            # if OAUTH1, get the real token string
            access_token = token_data.get('oauth_token', '')

        if uid and provider and access_token:
            token_data.pop('info', None)
            return cls.objects.update_or_create(
                uid=uid,
                provider=provider,
                defaults=dict(
                    user=user,
                    access_token=access_token,
                    secret=secret,
                    expires=(timezone.now() + datetime.timedelta(seconds=int(expires_in))) if expires_in else None,
                    data=token_data
                )
            )

        return None, False
