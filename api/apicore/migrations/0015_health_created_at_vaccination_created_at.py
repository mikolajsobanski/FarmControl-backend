# Generated by Django 4.2.2 on 2023-10-18 16:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0014_alter_costs_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='health',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 18, 16, 56, 38, 772672, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AddField(
            model_name='vaccination',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 18, 16, 56, 38, 773660, tzinfo=datetime.timezone.utc)),
        ),
    ]