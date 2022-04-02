from django.db import models
from models.contest import Contest
from models.problem import Problem


class ContestProblem(models.Model):
    contestid = models.ForeignKey(Contest, on_delete=models.PROTECT)
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    number = models.IntegerField()
    duration = models.IntegerField()

    class Meta:
        unique_together = ("contestid", "problemid")
