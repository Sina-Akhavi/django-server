from django.contrib import admin
from ..authentication.Models.user import User, UserAdmin
# Register your models here.

admin.site.register(User, UserAdmin)
