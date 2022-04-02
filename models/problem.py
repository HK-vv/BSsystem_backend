from django.db import models


class BSAdmin(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, unique=True, default="")
    password = models.CharField(max_length=20, default="123456")
    email = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=20, null=True)
