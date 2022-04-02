from django.db import models
from models.bsuser import BSUser
from models.contest import Contest
from models.problem import Problem


class Record(models.Model):
    userid = models.ForeignKey(BSUser, on_delete=models.PROTECT)
    contestid = models.ForeignKey(Contest, on_delete=models.PROTECT)
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    result = models.CharField(max_length=10, choices=[("正确", "正确"), ("错误", "错误"), ("未作答", "未作答")])
    submitted = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("userid", "contestid", "problemid")
