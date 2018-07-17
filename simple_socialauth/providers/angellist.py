from __future__ import unicode_literals

from .base import BaseProvider


# access tokens: no expiry
class AngellistProvider(BaseProvider):
    type = 'angellist'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://angel.co/api/oauth/authorize'
        self.access_token_url = 'https://angel.co/api/oauth/token'
        self.user_api_url = 'https://api.angel.co/1/me'
        super(AngellistProvider, self).__init__(**kwargs)

    def get_social_user_info(self):
        data = super(AngellistProvider, self).get_social_user_info()
        if data:
            name = data.get('name', '')
            name_split = name.split(' ', 1)
            uid = data.get('id')
            return {
                'source_data': data,
                'uid': uid,
                'username': uid,
                'name': name,
                'first_name': name_split[0],
                'last_name': name_split[1] if len(name_split) > 1 else ''
            }
        return {}


