# Generated by Django 4.2.2 on 2023-07-25 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiauth', '0003_forgot'),
    ]

    operations = [
        migrations.AddField(
            model_name='farmer',
            name='photo',
            field=models.ImageField(default='/user-image.png', upload_to=''),
        ),
    ]
