# Generated by Django 4.2.2 on 2023-08-01 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0004_farmer_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farmer',
            name='photo',
            field=models.ImageField(default='user-image.png', upload_to=''),
        ),
    ]