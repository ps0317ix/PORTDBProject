from django.contrib import admin
from .models import TwitterSender


@admin.register(TwitterSender)
class TwitterSenderAdmin(admin.ModelAdmin):
    list_display = ['screen_name', 'sender_id']

# admin.site.register(TwitterSender)
