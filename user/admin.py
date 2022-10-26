from django.contrib import admin
from user.models import User
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

# admin.site.register(User)
