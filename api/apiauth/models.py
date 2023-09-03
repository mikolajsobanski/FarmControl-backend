from django.contrib.auth.models import AbstractUser
from django.db import models

class Farmer(AbstractUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    username = None
    is_owner = models.BooleanField(default=True)
    id_owner = models.IntegerField(null=True)
    photo = models.ImageField(default='user-image.png')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class FarmerToken(models.Model):
    user_id = models.IntegerField()
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class Forgot(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)