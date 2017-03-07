from requests_oauthlib.compliance_fixes import linkedin_compliance_fix

from .base import BaseProvider


# access tokens: 60 day expiry
class LinkedinProvider(BaseProvider):
    type = 'linkedin'
    name = 'LinkedIn'

    def __init__(self, **kwargs):
        self.authorization_url = 'https://www.linkedin.com/uas/oauth2/authorization'
        self.access_token_url = 'https://www.linkedin.com/uas/oauth2/accessToken'
        super(LinkedinProvider, self).__init__(**kwargs)
        linkedin_compliance_fix(self.session)
        self.session.headers['x-li-format'] = 'json'

    def get_social_user_info(self):
        r = self.session.get('https://api.linkedin.com/v1/people/~:(id,first-name,last-name)')
        if r.status_code == 200:
            data = r.json()

            uid = data.get('id')
            first_name = data.get('firstName', '')
            last_name = data.get('lastName', '')
            name = "{0} {1}".format(first_name.strip(), last_name.strip()).strip()

            return {
                'source_data': data,
                'uid': uid,
                'username': uid,
                'name': name,
                'first_name': first_name,
                'last_name': last_name
            }
        return {}
