from django.db import models
from sender.models import TwitterSender


class TwitterReceiveDM(models.Model):
    sender = models.ForeignKey(TwitterSender, on_delete=models.CASCADE)
    receive_dm_sender_id = models.CharField(max_length=255)
    receive_dm_sender_name = models.CharField(max_length=255)
    msg_text = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'receive_dm'

    def __str__(self):
        return self.receive_dm_sender_name
