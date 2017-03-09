from __future__ import unicode_literals
from django.contrib import admin

from .models import SocialAccount


class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('uid', 'provider', 'user', 'expires')
    list_filter = ('provider', 'expires',)
    search_fields = ('user__email', 'user__id', 'user__username', 'access_token')
    readonly_fields = ('provider', 'uid', 'user')

admin.site.register(SocialAccount, SocialAccountAdmin)
