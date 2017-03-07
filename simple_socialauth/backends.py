from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend as StandardModelBackend

UserModel = get_user_model()


class Backend(StandardModelBackend):
    def authenticate(self, pk=None, social=False, **kwargs):
        if social:
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
