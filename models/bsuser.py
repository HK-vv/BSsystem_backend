from django.db import models


class BSUser(models.Model):
    openid = models.CharField(max_length=40, primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    rating = models.IntegerField(default=0)


