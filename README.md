### Overview

This social authentication Django app is unashamedly built on the shoulders of giants: specifically the excellent [`requests-oauthlib`](https://github.com/requests/requests-oauthlib) and [`requests`](https://github.com/kennethreitz/requests) modules.

Several opinionated decisions were made:
* do one thing: OAuth1/OAuth2 provider authentication
* avoid complexity by:
  * wrapping existing, trusted, and stable modules
  * letting the developer handle their own `User` model decisions and non-social login/registration

### Installation

Standard `pip` installation.

```
pip install django-simple-socialauth
```

This will automatically install `requests-oauthlib` as a requirement (and any modules it requires). Of course, you will need Django itself, obviously.

Add `simple_socialauth` to `INSTALLED_APPS` in your project's `settings.py`:

```
INSTALLED_APPS = (
    ...
    "simple_socialauth",
    ...
)
```

Add the `simple_socialauth` authentication backend to `AUTHENTICATION_BACKENDS` in your project's `settings.py`:

```
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'simple_socialauth.backends.Backend'
)
```

And finally, add the `simple_socialauth` URL patterns to your project's `urls.py`:

```
...
url_patterns = [
	...
    url(r'^oauth/', include('simple_socialauth.urls')),
	...
]
```

Run migrations:

```
python manage.py migrate
```

### Usage

With most OAuth API providers, you will need to add the callback URL for the given provider into your "app's" API settings with that provider. For example [Facebook's developer site](https://developers.facebook.com/) or [Twitter's developer site](https://dev.twitter.com/).

There are two scenarios for users passing through the `django-simple-socialauth` flow: registering and logging in.

#### User Registration

If the user doesn't exist in the system, `django-simple-socialauth` will create a new `User` and populate the first, last, email, and username fields with data it retrieves from the social provider's API. If possible, `django-simple-socialauth` will skip the 'completion form' step if all required information was retrieved - otherwise it is shown to the user to collect email and username as needed prior to `User` creation.

It then creates a [`SocialAccount`](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/models.py) instance representing the social provider's (ie. Facebook, Twitter, etc.) unique ID and access/refresh token data for the user. This `SocialAccount` is obviously associated with the new `User` via a foreign key.

Lastly, a `connect` signal is sent. This is an opportunity for the developer to hook into the social user registration process.

#### User Log in

If the user does exist in the system, `django-simple-socialauth` retrieves the existing `SocialAccount` and associated `User` - and updates the `SocialAccount` with the new access/refresh token data as needed.

A 'login' signal is sent, allowing the developer to hook into the social user login process.

#### After Authentication

The user's `SocialAccount` instance has a `session` property that sets up an appropriate OAuth1/2 authenticated `requests` session, which lets the developer access the social provider's API using the user's access_token, etc.

```
# assuming a Facebook SocialAccount object
r = social_account_obj.session.get('https://graph.facebook.com/me')
if r.ok:
    user_data = r.json()
    ...
```

### Configuration

`django-simple-socialauth` is quite configurable. Taking a look inside the module's [`settings`](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/settings.py) we find the following configuration options:

**`SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL`**

The URL pattern name or absolute URL to redirect to upon success. Defaults to `LOGIN_REDIRECT_URL` if set, else `/`.

**`SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL`**

The URL pattern name or absolute URL to redirect to upon error. Defaults to `/`.

**`SIMPLE_SOCIALAUTH_SITEROOT`**

The domain (eg `www.example.com`) to use when formatting OAuth URLs (ie. callbacks, etc). Defaults to `Site.objects.get_current().domain`.

**`SIMPLE_SOCIALAUTH_SECURE`**

This setting is only used when `SIMPLE_SOCIALAUTH_SITEROOT` is not set. In that case, `Site.objects.get_current().domain` is used for OAuth callbacks, but to form a proper URL, we need to know if it should be `http` vs `https`. Defaults to `True`.

**`SIMPLE_SOCIALAUTH_GENERATE_USERNAME`**

If True, when a new Django `User` needs to be created, `django-simple-socialauth` will automatically generate a unique username. Defaults to `False`, which causes the user to see a "Complete your registration" page with a form for username and email address.

Note that `django-simple-socialauth` will try to use email and username information from the social provider for these fields first - if they are not available or are already used in the system, the 'completion' form will display.

**`SIMPLE_SOCIALAUTH_PROVIDERS`**

This setting indicates which social provider modules are enabled. Defaults to `()` (ie. no providers enabled). This setting works together with `SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS`, meaning you will need to add corresponding settings there. Enabling providers is simple - in your Django project `settings.py`, to enable both Facebook and Twitter, just add:

```
SIMPLE_SOCIALAUTH_PROVIDERS = (
	'simple_socialauth.providers.facebook.FacebookProvider',
	'simple_socialauth.providers.twitter.TwitterProvider'
)
```

Note that this method of enabling providers allows the developer to [create custom social providers](#custom-providers).

See below for a [list of included social providers](#provider-list).

**`SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS`**

All social providers require an API `id` (sometimes called a `key`) and `secret`. Assuming Facebook (OAuth2) and Twitter (OAuth1) providers are enabled, this is how their settings would be configured:

```
SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS = {
    'twitter': {
        'init_params': {
            'client_key': 'twitter-key',
            'client_secret': 'twitter-secret'
        },
        'authorize_params': {},
        'callback_params': {}
    },
    'facebook': {
        'init_params': {
            'client_id': 'facebook-client_id',
            # 'scope': ['email', 'public_profile', 'user_friends']

        },
        'authorize_params': {},
        'callback_params': {
            'client_secret': 'facebook-client_secret'
        }
    }
}
```

Notice that authorization `scope` can also be set in each provider's `init_params`. The details of each provider's `scope` options is out of the scope of this documentation - and is subject to change.

All OAuth2-based providers will follow the format show by the Facebook example above. OAuth1-based providers will follow the example shown by Twitter above.


### Notes

#### OAuth Scope Advice

When selecting which OAuth `scopes` for your enabled providers in `SIMPLE_SOCIALAUTH_PROVIDERS_SETTINGS`, consider adding the scopes that get you both the username and email address for the authenticating user. This will allow the user to skip the cumbersome 'completion form' step that asks them to fill those fields in.

#### Included Social Providers <a name='provider-list'></a>

All are OAuth2 unless indicated:

* `facebook`: `simple_socialauth.providers.facebook.FacebookProvider`
* `twitter`: `simple_socialauth.providers.twitter.TwitterProvider` (**OAuth1**)
* `github`: `simple_socialauth.providers.github.GithubProvider`
* `pinterest`: `simple_socialauth.providers.pinterest.PinterestProvider`
* `google`: `simple_socialauth.providers.google.GoogleProvider`
* `linkedin`: `simple_socialauth.providers.linkedin.LinkedinProvider`
* `angellist`: `simple_socialauth.providers.angellist.AngellistProvider`


#### Creating Custom Providers <a name='custom-providers'></a>

If the social provider you want to add is OAuth1 or OAuth2 based, then `requests-oauthlib` almost certainly supports it. There are some that aren't fully OAuth1/2 compliant, and thus `requests-oauthlib` has a number of [compliance fixes](https://github.com/requests/requests-oauthlib/tree/master/requests_oauthlib/compliance_fixes). This project uses the [Facebook](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/providers/facebook.py) and [LinkedIn](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/providers/linkedin.py) fixes, for example.

Creating a custom provider is quite simple - let's take a look at the [Github provider](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/providers/github.py) to see what's involved:

```
from .base import BaseProvider


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
                'company': data.get('company', ''),
                'organizations_url': data.get('organizations_url', ''),
                'repositories_url': data.get('repos_url', ''),
                'name': name,
                'first_name': name_split[0],
                'last_name': name_split[1] if len(name_split) > 1 else ''
            }
        return {}
```

Each provider must inherit from `BaseProvider` and requires a unique `type` value.

For display purposes, a `name` value can be optionally set, but will fall back on `type`. This is useful for providers whose names aren't easily title-cased, such as "LinkedIn" (note the capital 'I').

The appropriate OAuth1/2 URLs must be set:

* `authorization_url` (OAuth1/2)
* `access_token_url` (OAuth1/2)
* `request_token_url` (OAuth1 only - see the [Twitter provider](https://github.com/jaddison/django-simple-socialauth/blob/master/simple_socialauth/providers/twitter.py))
* `user_api_url` (OAuth1/2)

Any compliance fixes ought to be done at the end of the provider's `__init__`.

Upon successful user authentication via a provider, `django-simple-socialauth` calls the provider's `get_social_user_info()` method, which retrieves key user-specific information from the social provider's authenticated API. This method should return the following information (if available) in a `dict`:

* `uid` the social provider's unique ID for the user in their system (required!)
* `username`
* `email`
* `first_name`
* `last_name`

This information is used to create the Django `User`.
