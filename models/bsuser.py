from django.db import models


class BSUser(models.Model):
    openid = models.CharField(max_length=30, primary_key=True)
    username = models.CharField(max_length=20, unique=True, default="")
    rating = models.IntegerField(default=0)


