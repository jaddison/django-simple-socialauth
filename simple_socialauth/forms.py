from django import forms
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .settings import SIMPLE_SOCIALAUTH_GENERATE_USERNAME

User = get_user_model()


class UserCreateCleanMixin(object):
    def clean_email(self):
        instance = getattr(self, 'instance')
        email = self.cleaned_data.get('email', '').lower().strip()

        qs = User.objects.filter(email__iexact=email)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                self.error_messages['email_unique'],
                code='email_unique'
            )

        return email

    def clean_username(self):
        instance = getattr(self, 'instance')
        username = self.cleaned_data.get('username', '').strip()

        qs = User.objects.filter(username__iexact=username)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise forms.ValidationError(
                self.error_messages['username_unique'],
                code='username_unique'
            )

        return username


def create_model_form():
    class _PostSocialSignupForm(UserCreateCleanMixin, forms.ModelForm):
        error_messages = {
            'email_unique': _("A user with that email address already exists."),
            'username_unique': _("A user with that username already exists.")
        }

        class Meta:
            model = User
            fields = ('username', 'email')

    # only process fields which exist in the User model; if a custom
    # User model is defined without a `username` field, this lets us
    # still use this modelform
    # also, if SIMPLE_SOCIALAUTH_GENERATE_USERNAME is True, we don't
    # want this form to do anything with `username` (we'll generate it)
    available_model_fields = [f.name for f in User._meta.get_fields() if f.name != 'username' or not SIMPLE_SOCIALAUTH_GENERATE_USERNAME]
    _PostSocialSignupForm.Meta.fields = [f for f in _PostSocialSignupForm.Meta.fields if f in available_model_fields]
    return type('PostSocialSignupForm', (_PostSocialSignupForm,), {})

# This moderately terrible way of creating the modelform is needed to
# account for the possibility that developers may have a custom model
# that does not include a `username` field - the assumption IS made
# however that there is always an `email` field.
PostSocialSignupForm = create_model_form()