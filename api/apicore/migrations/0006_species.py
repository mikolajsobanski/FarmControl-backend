# Generated by Django 4.2.2 on 2023-09-06 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0005_alter_task_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='Species',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('lifetime', models.CharField(max_length=50)),
                ('avg_age', models.IntegerField()),
                ('nutrition', models.CharField(max_length=200)),
                ('photo', models.ImageField(upload_to='')),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('avg_weight', models.CharField(max_length=50)),
                ('sex', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=50)),
            ],
        ),
    ]