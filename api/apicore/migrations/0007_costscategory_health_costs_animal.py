# Generated by Django 4.2.2 on 2023-09-07 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0006_species'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostsCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Health',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Costs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apicore.costscategory')),
            ],
        ),
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('photo', models.ImageField(upload_to='')),
                ('owner', models.IntegerField()),
                ('dob', models.DateTimeField()),
                ('costs', models.ManyToManyField(related_name='animal_costs', to='apicore.costs')),
                ('health', models.ManyToManyField(related_name='animal_health', to='apicore.health')),
                ('species', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apicore.species')),
            ],
        ),
    ]
