from __future__ import unicode_literals

from .base import BaseProvider


# access tokens: 60 day expiry
class GithubProvider(BaseProvider):
    type = 'github'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://github.com/login/oauth/authorize'
        self.access_token_url = 'https://github.com/login/oauth/access_token'
        self.user_api_url = 'https://api.github.com/user'
        super(GithubProvider, self).__init__(**kwargs)

    def get_social_user_info(self):
        data = super(GithubProvider, self).get_social_user_info()
        if data:
            uid = data.get('id')
            name = data.get('name', '')
            name_split = name.split(' ', 1)
            return {
                'source_data': data,
                'uid': uid,
                'username': data.get('login', ''),
                'email': data.get('email', ''),
                'name': name,
                'first_name': name_split[0],
                'last_name': name_split[1] if len(name_split) > 1 else ''
            }
        return {}