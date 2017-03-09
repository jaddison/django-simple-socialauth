from __future__ import unicode_literals

from .base import BaseProvider


# access tokens: no expiry
class TwitterProvider(BaseProvider):
    type = 'twitter'

    def __init__(self, **kwargs):
        # use authenticate instead of authorize as the latter forces the user
        # to accept permissions each time as per the oauth spec (?)
        # self.authorization_url = 'https://api.twitter.com/oauth/authorize'
        self.authorization_url = 'https://api.twitter.com/oauth/authenticate'
        self.request_token_url = 'https://api.twitter.com/oauth/request_token'
        self.access_token_url = 'https://api.twitter.com/oauth/access_token'
        super(TwitterProvider, self).__init__(True,  **kwargs)

    def get_social_user_info(self):
        r = self.session.get('https://api.twitter.com/1.1/account/verify_credentials.json')
        if r.status_code == 200:
            data = r.json()
            name = data.get('name', '')
            name_split = name.split(' ', 1)
            return {
                'source_data': data,
                'uid': data.get('id'),
                'username': data.get('screen_name', ''),
                'timezone': float(data.get('utc_offset', 0) or 0) / 3600,
                'language': data.get('lang', '').lower(),
                'name': name,
                'first_name': name_split[0],
                'last_name': name_split[1] if len(name_split) > 1 else ''
            }
        return {}