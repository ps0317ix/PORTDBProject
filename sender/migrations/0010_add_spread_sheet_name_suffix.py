# Generated by Django 3.2.11 on 2022-07-11 21:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0009_change_GCP_account_key_upload_default'),
    ]

    operations = [
        migrations.AddField(
            model_name='twittersender',
            name='spread_sheet_name_suffix',
            field=models.CharField(default='', max_length=50),
        ),
    ]