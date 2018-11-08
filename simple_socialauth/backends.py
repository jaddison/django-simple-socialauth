from __future__ import unicode_literals
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as StandardModelBackend

from .models import SocialAccount

UserModel = get_user_model()


class Backend(StandardModelBackend):
    def authenticate(self, request, social=False, **kwargs):
        if social:
            uid = kwargs.get('uid', '')
            provider = kwargs.get('provider', '')
            if uid and provider:
                try:
                    return SocialAccount.objects.select_related('user').get(
                        uid=uid, provider=provider
                    ).user
                except SocialAccount.DoesNotExist:
                    pass

            pk = kwargs.get('pk')
            if pk:
                try:
                    user = UserModel.objects.get(pk=pk)
                except UserModel.DoesNotExist:
                    # Run the default password hasher once to reduce the timing
                    # difference between an existing and a nonexistent user (#20760).
                    UserModel().set_password(None)
                else:
                    # `user_can_authenticate` only appeared in Django 1.10, so
                    # ignore it if it doesn't exist for lower versions' sakes
                    if not hasattr(self, 'user_can_authenticate') or self.user_can_authenticate(user):
                        return user
