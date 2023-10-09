# Generated by Django 4.2.2 on 2023-09-17 13:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apicore', '0008_remove_species_sex_animal_sex'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animal',
            name='costs',
        ),
        migrations.RemoveField(
            model_name='animal',
            name='health',
        ),
        migrations.AddField(
            model_name='animal',
            name='animal_costs',
            field=models.ManyToManyField(related_name='costs', to='apicore.costs'),
        ),
        migrations.AddField(
            model_name='animal',
            name='animal_health',
            field=models.ManyToManyField(related_name='health', to='apicore.health'),
        ),
        migrations.AddField(
            model_name='costs',
            name='animal',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='apicore.animal'),
        ),
        migrations.AddField(
            model_name='health',
            name='animal',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='apicore.animal'),
        ),
        migrations.CreateModel(
            name='Vaccination',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('date', models.DateTimeField()),
                ('expiration_date', models.DateTimeField()),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apicore.animal')),
            ],
        ),
        migrations.AddField(
            model_name='animal',
            name='animal_vaccination',
            field=models.ManyToManyField(related_name='vaccination', to='apicore.vaccination'),
        ),
    ]