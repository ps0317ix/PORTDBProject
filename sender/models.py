from django.db import models
from user.models import User


class TwitterSender(models.Model):
    sender_id = models.CharField(max_length=100, unique=True)
    screen_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    spread_sheet_id = models.CharField(max_length=100)
    spread_sheet_name_suffix = models.CharField(max_length=50, default='')
    CONSUMER_KEY = models.CharField(max_length=100, unique=True)
    CONSUMER_SECRET = models.CharField(max_length=100, unique=True)
    ACCESS_TOKEN = models.CharField(max_length=100, unique=True)
    ACCESS_TOKEN_SECRET = models.CharField(max_length=100, unique=True)
    gcp_api_key = models.CharField(max_length=100)
    GCP_account_key_upload = models.FileField(default='GCP_account_keys/port-v2-service-account-key.json', upload_to='GCP_account_keys/')
    bq_project_id = models.CharField(max_length=100)
    bq_dataset_id = models.CharField(max_length=100)
    user = models.ManyToManyField(User)
    is_zendesk = models.BooleanField(default=False)
    zendesk_email = models.CharField(max_length=50, default='')
    zendesk_subdomain = models.CharField(max_length=50, default='')
    zendesk_api_key = models.CharField(max_length=50, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'twitter_sender'

    def __str__(self):
        return self.screen_name
