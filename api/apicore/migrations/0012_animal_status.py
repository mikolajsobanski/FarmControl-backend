# Generated by Django 4.2.2 on 2023-10-05 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0011_alter_costs_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='animal',
            name='status',
            field=models.BooleanField(default=True),
        ),
    ]
