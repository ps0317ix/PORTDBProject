from django.db import models
import datetime


class Server(models.Model):
    name = models.CharField(max_length=30)
    base_url = models.URLField()
    basic_user = models.CharField(max_length=30)
    basic_password = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'server'

    def __str__(self):
        return self.name
