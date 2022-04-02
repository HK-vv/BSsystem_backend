from django.db import models
from models.bsadmin import BSAdmin


class Problem(models.Model):
    id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=200, blank=True)
    type = models.CharField(max_length=20, default="单选",
                            choices=[("single", "单选"), ("multiple", "多选"), ("completion", "填空"), ("binary", "判断")])
    A = models.CharField(max_length=50, null=True)
    B = models.CharField(max_length=50, null=True)
    C = models.CharField(max_length=50, null=True)
    D = models.CharField(max_length=50, null=True)
    answer = models.CharField(max_length=100)
    public = models.BooleanField()
    authorid = models.ForeignKey(BSAdmin, on_delete=models.PROTECT)
