# Generated by Django 3.2.11 on 2022-02-25 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_add_is_account_analyze'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.ImageField(blank=True, upload_to='', verbose_name='avatar'),
        ),
    ]