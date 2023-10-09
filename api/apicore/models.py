from django.db import models

# Create your models here.

class Note(models.Model):
    owner = models.IntegerField()
    title = models.CharField(max_length=200)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

class TaskComment(models.Model):
    owner = models.IntegerField()
    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Task(models.Model):
    owner = models.IntegerField()
    worker = models.IntegerField()
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    content = models.TextField()
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comments = models.ManyToManyField(TaskComment, related_name='task_comments')

class Species(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    lifetime = models.CharField(max_length=50)
    avg_age = models.IntegerField()
    nutrition = models.CharField(max_length=200)
    photo = models.ImageField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    avg_weight = models.CharField(max_length=50)
    type = models.CharField(max_length=50)

class Health(models.Model):
    name = models.CharField(max_length=200, default='')
    description = models.TextField()
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, default=None)

class Vaccination(models.Model):
    name = models.CharField(max_length=200)
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE)
    date = models.DateTimeField()
    expiration_date = models.DateTimeField()

class CostsCategory(models.Model):
    name = models.CharField(max_length=50)

class Costs(models.Model):
    name = models.CharField(max_length=250)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(CostsCategory, on_delete=models.CASCADE)
    animal = models.ForeignKey('Animal', on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

class Animal(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField()
    species = models.ForeignKey(Species, on_delete=models.CASCADE)
    animal_health = models.ManyToManyField(Health, related_name='health')
    animal_costs = models.ManyToManyField(Costs, related_name='costs')
    animal_vaccination = models.ManyToManyField(Vaccination, related_name="vaccination")
    owner = models.IntegerField()
    dob = models.DateTimeField()
    sex = models.CharField(max_length=50, default='male/female')
    status = models.BooleanField(default=True)