# Generated by Django 4.2.2 on 2023-10-08 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0013_costs_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costs',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]