# Generated by Django 4.2.2 on 2023-08-12 11:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0004_taskcomment_owner_alter_task_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='owner',
            field=models.IntegerField(),
        ),
    ]
