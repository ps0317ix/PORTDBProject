# Generated by Django 3.2.11 on 2022-10-03 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0020_add_is_top_liver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_top_liver',
        ),
        migrations.AddField(
            model_name='user',
            name='rank',
            field=models.CharField(blank=True, default='', max_length=20, null=True),
        ),
    ]
