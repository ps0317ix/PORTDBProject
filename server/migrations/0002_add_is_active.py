# Generated by Django 3.2.11 on 2022-02-09 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_add_server'),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
