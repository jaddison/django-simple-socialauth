from __future__ import unicode_literals
from requests_oauthlib.compliance_fixes import facebook_compliance_fix

from .base import BaseProvider


# access tokens: 60 day expiry
class FacebookProvider(BaseProvider):
    type = 'facebook'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://www.facebook.com/dialog/oauth'
        self.access_token_url = 'https://graph.facebook.com/oauth/access_token'
        super(FacebookProvider, self).__init__(**kwargs)
        facebook_compliance_fix(self.session)

    def get_social_user_info(self):
        r = self.session.get('https://graph.facebook.com/me')
        if r.status_code == 200:
            data = r.json()
            uid = data.get('id')
            return {
                'source_data': data,
                'uid': uid,
                'username': data.get('username', ''),
                'timezone': float(data.get('timezone', 0)),
                'gender': data.get('gender', ''),
                'language': data.get('locale', '').split('_')[0].lower(),
                'name': data.get('name', ''),
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'email': data.get('email', '')
            }
        return {}
