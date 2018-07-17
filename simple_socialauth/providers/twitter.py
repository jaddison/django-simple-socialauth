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
        self.user_api_url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        super(TwitterProvider, self).__init__(True,  **kwargs)

    def get_social_user_info(self):
        data = super(TwitterProvider, self).get_social_user_info()
        if data:
            name = data.get('name', '')
            name_split = name.split(' ', 1)
            return {
                'source_data': data,
                'uid': data.get('id'),
                'username': data.get('screen_name', ''),
                'name': name,
                'first_name': name_split[0],
                'last_name': name_split[1] if len(name_split) > 1 else ''
            }
        return {}