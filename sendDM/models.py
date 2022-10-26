from django.db import models
from sender.models import TwitterSender
from google.cloud import bigquery


class TwitterSendDM(models.Model):
    sender_screen_name = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50)
    target_name = models.CharField(max_length=50)
    target_screen_name = models.CharField(max_length=50)
    target_description = models.TextField()
    target_follow_count = models.IntegerField(default=0)
    target_followers_count = models.IntegerField(default=0)
    content = models.TextField()
    send_result = models.CharField(max_length=10)
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    schema = [
        bigquery.SchemaField('sender_screen_name', 'STRING', mode='REQUIRED', description='送信アカウント名'),
        bigquery.SchemaField('email', 'STRING', mode='REQUIRED', description='メールアドレス'),
        bigquery.SchemaField('target_id', 'STRING', mode='REQUIRED', description='対象ID'),
        bigquery.SchemaField('target_name', 'STRING', mode='REQUIRED', description='対象アカウント'),
        bigquery.SchemaField('target_screen_name', 'STRING', mode='REQUIRED', description='対象スクリーン名'),
        bigquery.SchemaField('target_description', 'STRING', mode='REQUIRED', description='対象プロフィール文'),
        bigquery.SchemaField('target_follow_count', 'INTEGER', mode='REQUIRED', description='対象フォロー数'),
        bigquery.SchemaField('target_followers_count', 'INTEGER', mode='REQUIRED', description='対象フォロワー数'),
        bigquery.SchemaField('content', 'STRING', mode='NULLABLE', description='送信対象ID'),
        bigquery.SchemaField('send_result', 'STRING', mode='NULLABLE', description='送信結果'),
        bigquery.SchemaField('response', 'STRING', mode='NULLABLE', description='返信'),
        bigquery.SchemaField('created_at', 'DATETIME', mode='REQUIRED', description='作成日'),
        bigquery.SchemaField('updated_at', 'DATETIME', mode='REQUIRED', description='更新日')
    ]

    class Meta:
        db_table = 'twitter_send_dm'

    def __str__(self):
        return self.content
