# Generated by Django 3.2.11 on 2022-06-29 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0008_add_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twittersender',
            name='GCP_account_key_upload',
            field=models.FileField(default='GCP_account_keys/port-v2-service-account-key.json', upload_to='GCP_account_keys/'),
        ),
    ]
