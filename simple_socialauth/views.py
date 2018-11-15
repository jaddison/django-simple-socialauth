from __future__ import unicode_literals
import datetime
import hashlib

from django.contrib import messages
from django.contrib.auth import login as auth_login, authenticate, get_user_model
from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.views.generic import View
from django.utils import six

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from . import signals
from .forms import PostSocialSignupForm
from .models import SocialAccount
from .providers import registry
from .settings import SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL, SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL, \
    SIMPLE_SOCIALAUTH_GENERATE_USERNAME


class BaseView(View):
    http_method_names = ['get']

    def dispatch(self, request, *args, **kwargs):
        provider_type = kwargs.get('provider_type', '')
        provider = registry.get(provider_type)

        if not provider:
            return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)

        kwargs['provider'] = provider

        return super(BaseView, self).dispatch(request, *args, **kwargs)


class LoginView(BaseView):
    def get(self, request, provider_type, provider, *args, **kwargs):
        kw = {}
        if 'force' in request.GET:
            kw['force'] = True

        next_url = request.GET.get('next', '')
        if next_url:
            request.session['simple_socialauth:next_url'] = next_url

        # get the auth url and redirect the user to it to accept/decline
        return redirect(provider.connect(**kw))


class CallbackView(BaseView):
    def get(self, request, provider_type, provider, *args, **kwargs):
        error = request.GET.get('error')
        if error:
            if error == 'access_denied':
                # user clicked cancel on the facebook dialog
                messages.warning(request,
                                 "You declined the {0} authentication request. Shame!".format(provider_type.title()))
            else:
                messages.warning(request,
                                 "Something went wrong with the {0} authentication request. Perhaps try again?".format(
                                     provider_type.title()))

            return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)

        # process the callback information into a token (the current
        # provider session is auto updated to use the token data)
        try:
            token_data = provider.callback(request.build_absolute_uri())
        except Exception as e:
            # this can fail due to the user denying it; some oauth providers
            # don't pass back the spec-required parameters expected by the
            # oauth lib we use, it blows up - so catch the error and fall back
            # to 'not' authorized.
            token_data = None

        if token_data:
            # List of the possible fields we might get from the various social providers;
            # uid = username = email = name = first_name = last_name = timezone = gender = language = ''

            user_info = provider.get_social_user_info()
            if user_info and 'uid' in user_info:
                user_info['provider'] = provider_type

                # Do we already have a user matching the social provider user id? if so, log in the
                # corresponding Django user.
                try:
                    account = SocialAccount.objects.select_related('user').get(
                        provider=provider_type,
                        uid=user_info.get('uid')
                    )
                except SocialAccount.DoesNotExist:
                    account = None

                if account:
                    if request.user.is_authenticated:
                        if request.user.id != account.user_id:
                            messages.error(request, "This {0} account is associated with another user.".format(
                                provider.display_name()))
                            return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)
                    else:
                        user = authenticate(pk=account.user_id, social=True)
                        if not user:
                            # `user` will be None if the user is not allowed by `authenticate()` above
                            messages.error(request, "Unable to log in.")
                            return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)

                        auth_login(request, user)
                elif provider_type == 'google' and 'refresh_token' not in token_data:
                    # special case for google auth - we need to force a re-auth to ensure we get a refresh_token
                    return redirect(reverse('simple_socialauth-login', args=(provider_type,)) + '?force=1')

                if not request.user.is_authenticated:
                    # we need to redirect the user to another page in order to complete
                    # some signup details - save the social user info to the session
                    # for later use
                    request.session['simple_socialauth:user_info'] = user_info
                    request.session['simple_socialauth:token_data'] = token_data
                    return redirect(reverse('simple_socialauth-login_complete', args=(provider_type,)))

                account, created = SocialAccount.create_or_update(request.user, user_info, token_data)

                signals.login.send(
                    SocialAccount,
                    request=request,
                    account=account,
                    user_info=user_info,
                    created=created
                )
                next_url = request.session.pop('simple_socialauth:next_url', '') or SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL
                return redirect(next_url)

        return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)


class CompleteView(BaseView):
    http_method_names = ['get', 'post']
    form_class = PostSocialSignupForm

    def get(self, *args, **kwargs):
        return self._handler(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self._handler(*args, **kwargs)

    def _handler(self, request, provider_type, provider, *args, **kwargs):
        user_info = request.session.get('simple_socialauth:user_info', {})

        email = user_info.get('email', '').lower().strip()
        username = user_info.get('username', '').strip()

        # we can't legitimately be here if:
        # - we're logged in or
        # - don't have have user_info
        if not user_info or request.user.is_authenticated:
            return redirect(SIMPLE_SOCIALAUTH_LOGIN_ERROR_REDIRECT_URL)

        kw = {
            'username': username,
            'email': email
        }

        if request.method == 'GET':
            # first try to save a new user with their username and email
            # from the social provider; if it fails is_valid() below
            # it probably means data is missing or a matching user already
            # exists for email or username
            form = self.form_class(kw)
        else:
            form = self.form_class(request.POST, initial=kw)

        if form.is_valid():
            user = form.save(commit=False)

            if hasattr(user, 'first_name'):
                user.first_name = user_info.get('first_name') or ''
            if hasattr(user, 'last_name'):
                user.last_name = user_info.get('last_name') or ''
            user.set_unusable_password()

            needs_username = hasattr(user, 'username')
            # loop to allow for race condition induced IntegrityErrors
            # (ie. unique username/email are taken before .save() is
            # called
            while True:
                if needs_username and not user.username and SIMPLE_SOCIALAUTH_GENERATE_USERNAME:
                    h = hashlib.sha256()
                    h.update(six.text_type(user_info.get('uid', '')).encode('utf8'))
                    h.update(provider_type.encode('utf8'))
                    h.update(email.encode('utf8'))
                    h.update(six.text_type(datetime.datetime.now()).encode('utf8'))
                    user.username = h.hexdigest()[:user._meta.get_field('username').max_length]

                try:
                    user.save()
                    break
                except IntegrityError:
                    if not needs_username or not user.__class__.objects.filter(username=user.username).exists():
                        # if there isn't a matching user with the same username
                        # already, then it's an IntegrityError for something other
                        # than the the username field - re-raise as we won't handle it.
                        raise
                    user.username = ''

            # clean up the session
            request.session.pop('simple_socialauth:user_info', {})
            token_data = request.session.pop('simple_socialauth:token_data', {})

            user = authenticate(pk=user.pk, social=True)
            auth_login(request, user)

            account, created = SocialAccount.create_or_update(user, user_info, token_data)

            signals.connect.send(
                SocialAccount,
                request=request,
                account=account,
                user_info=user_info,
                created=created
            )

            return redirect(
                request.session.pop('simple_socialauth:next_url', '') or SIMPLE_SOCIALAUTH_LOGIN_SUCCESS_REDIRECT_URL
            )

        context = {
            'form': form
        }

        return render(request, 'simple_socialauth/login_complete.html', context)
