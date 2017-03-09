from __future__ import unicode_literals
from django.conf import settings

SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL = getattr(settings, 'SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL', None) or getattr(settings, 'LOGIN_REDIRECT_URL', '/')
SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL = getattr(settings, 'SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL', '/')
SIMPLE_SOCIALAUTH_PROVIDERS = getattr(settings, 'SIMPLE_SOCIALAUTH_PROVIDERS', ())
SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS = getattr(settings, 'SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS', {})
SIMPLE_SOCIALAUTH_SITEROOT = getattr(settings, 'SIMPLE_SOCIALAUTH_SITEROOT', '')
SIMPLE_SOCIALAUTH_SECURE = getattr(settings, 'SIMPLE_SOCIALAUTH_SECURE', True)
SIMPLE_SOCIALAUTH_GENERATE_USERNAME = getattr(settings, 'SIMPLE_SOCIALAUTH_GENERATE_USERNAME', False)

""" Example data for currently supported providers - put something like this in your Django project's settings.py:

SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS = {
    'twitter': {
        'init_params': {
            'client_key': 'my-key',
            'client_secret': 'my-secret'
        },
        'authorize_params': {},
        'callback_params': {}
    },
    'facebook': {
        'init_params': {
            'client_id': 'my-client_id',
            # 'scope': ['manage_pages', 'publish_stream']
        },
        'authorize_params': {},
        'callback_params': {
            'client_secret': 'my-client_secret'
        }
    },
    'google': {
        'init_params': {
            'client_id': 'my-client_id',
            'auto_refresh_url': 'https://accounts.google.com/o/oauth2/token',
            # see https://www.googleapis.com/discovery/v1/apis/oauth2/v2/rest?fields=auth(oauth2(scopes))
            'scope': ['https://www.googleapis.com/auth/plus.login']
        },
        'authorize_params': {
            'access_type': 'offline'
        },
        'callback_params': {
            'client_secret': 'my-client_secret'
        }
    },
    'github': {
        'init_params': {
            'client_id': 'my-client_id',
            # 'scope': ['manage_pages', 'publish_stream']
        },
        'authorize_params': {},
        'callback_params': {
            'client_secret': 'my-client_secret'
        }
    },
    'angellist': {
        'init_params': {
            'client_id': 'my-client_id'
        },
        'callback_params': {
            'client_secret': 'my-client_secret'
        }
    },
    'linkedin': {
        'init_params': {
            'client_id': 'my-client_id'
        },
        'callback_params': {
            'client_secret': 'my-client_secret'
        }
    }
}
"""
