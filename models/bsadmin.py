from django.contrib.auth.models import AbstractUser
from django.db import models


class BSAdmin(AbstractUser):
    DEFAULT_PASSWORD = '123456'

    password = models.CharField(max_length=20, default=DEFAULT_PASSWORD)
    email = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=20, null=True)
