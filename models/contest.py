from django.db import models
from models.bsadmin import BSAdmin


class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    start = models.DateTimeField()
    latest = models.DateTimeField()
    password = models.CharField(max_length=30, null=True)
    rated = models.BooleanField()
    authorid = models.ForeignKey(BSAdmin, on_delete=models.PROTECT)
