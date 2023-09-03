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