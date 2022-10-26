# Generated by Django 3.2.11 on 2022-08-01 05:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sender', '0010_add_spread_sheet_name_suffix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='twittersender',
            name='bq_dataset_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='twittersender',
            name='bq_project_id',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='twittersender',
            name='password',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='twittersender',
            name='screen_name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='twittersender',
            name='sender_id',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='twittersender',
            name='spread_sheet_id',
            field=models.CharField(max_length=100),
        ),
    ]
