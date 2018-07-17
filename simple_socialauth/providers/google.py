from __future__ import unicode_literals

from .base import BaseProvider


# access tokens: relatively short-lived, but auto refreshes if set up correctly
class GoogleProvider(BaseProvider):
    type = 'google'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://accounts.google.com/o/oauth2/auth'
        self.access_token_url = 'https://accounts.google.com/o/oauth2/token'
        self.user_api_url = 'https://www.googleapis.com/plus/v1/people/me'
        super(GoogleProvider, self).__init__(**kwargs)

    def connect(self, **kwargs):
        force = kwargs.pop('force', None)
        if force:
            # we need to force the user to re-auth our app (ie. click
            # accept on the Google auth page) - most likely because
            # we need a new refresh_token
            kwargs['approval_prompt'] = 'force'
        return super(GoogleProvider, self).connect(**kwargs)

    def get_social_user_info(self):
        data = super(GoogleProvider, self).get_social_user_info()
        if data:
            uid = data.get('id')
            email = ''
            for tmp in data.get('emails', []):
                if tmp.get('type', '') == 'account':
                    email = tmp.get('email', '')
                    break

            return {
                'source_data': data,
                'uid': uid,
                'username': uid,
                'name': data.get('displayName', ''),
                'first_name': data.get('name', {}).get('givenName', ''),
                'last_name': data.get('name', {}).get('familyName', ''),
                'email': email
            }
        return {}
