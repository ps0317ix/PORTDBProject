# Generated by Django 3.2.11 on 2022-06-26 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_change_upload_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='line_id',
            field=models.CharField(default='', max_length=20),
        ),
    ]