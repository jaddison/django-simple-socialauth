from __future__ import unicode_literals
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from .base import BaseProvider


# access tokens: 60 day expiry
class FacebookProvider(BaseProvider):
    type = 'facebook'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://www.facebook.com/dialog/oauth'
        self.access_token_url = 'https://graph.facebook.com/oauth/access_token'
        self.user_api_url = 'https://graph.facebook.com/me'
        super(FacebookProvider, self).__init__(**kwargs)
        facebook_compliance_fix(self.session)

    def get_social_user_info(self):
        data = super(FacebookProvider, self).get_social_user_info()
        if data:
            uid = data.get('id')
            return {
                'source_data': data,
                'uid': uid,
                'email': data.get('email', ''),
                'name': data.get('name', ''),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
            }
        return {}
