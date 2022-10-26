from django.db import models
from user.models import User
from sender.models import TwitterSender


class TwitterSendContent(models.Model):
    user = models.ManyToManyField(User)
    sender = models.ManyToManyField(TwitterSender)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'twitter_send_content'

    def __str__(self):
        return self.content
