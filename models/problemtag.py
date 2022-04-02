from django.db import models
from models.problem import Problem
from models.tag import Tag


class ProblemTag(models.Model):
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    tagid = models.ForeignKey(Tag, on_delete=models.PROTECT)

