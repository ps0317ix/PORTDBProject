from django.db import models
from user.models import User


class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(verbose_name='メールアドレス', max_length=255, default="")
    type = models.JSONField(default=dict)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contact'

    def __str__(self):
        return self.name
