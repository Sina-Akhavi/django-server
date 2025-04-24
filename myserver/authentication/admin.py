from django.contrib import admin

from authentication.models import User, UserAdmin

admin.site.register(User, UserAdmin)
