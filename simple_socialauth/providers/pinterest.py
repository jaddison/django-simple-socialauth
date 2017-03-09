from __future__ import unicode_literals

from .base import BaseProvider


class PinterestProvider(BaseProvider):
    type = 'pinterest'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://api.pinterest.com/oauth/'
        self.access_token_url = 'https://api.pinterest.com/v1/oauth/token'
        super(PinterestProvider, self).__init__(**kwargs)

    def get_social_user_info(self):
        r = self.session.get('https://api.pinterest.com/v1/me/?fields=id,username,first_name,last_name')
        if r.status_code == 200:
            data = r.json().get('data')
            uid = data.get('id')

            return {
                'source_data': data,
                'uid': uid,
                'username': data.get('username', ''),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', '')
            }
        return {}
