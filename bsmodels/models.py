from django.contrib.auth.models import AbstractUser
from django.db import models


class BSUser(models.Model):
    openid = models.CharField(max_length=40, primary_key=True)
    username = models.CharField(max_length=20, unique=True)
    rating = models.IntegerField(default=0)


class BSAdmin(AbstractUser):
    DEFAULT_PASSWORD = '123456'

    username = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=20, default=DEFAULT_PASSWORD)
    email = models.CharField(max_length=30, null=True)
    phone = models.CharField(max_length=20, null=True)

    REQUIRED_FIELDS = []  # ['username']

    USERNAME_FIELD = 'username'

    class Meta:
        ordering = ['id']


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
    # tags = models.ManyToManyField(Tag, through=ProblemTag)


class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    start = models.DateTimeField()
    latest = models.DateTimeField()
    password = models.CharField(max_length=30, null=True)
    rated = models.BooleanField()
    authorid = models.ForeignKey(BSAdmin, on_delete=models.PROTECT)
    # problems = models.ManyToManyField(Problem, through=ContestProblem)


class ContestProblem(models.Model):
    contestid = models.ForeignKey(Contest, on_delete=models.PROTECT)
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    number = models.IntegerField()
    duration = models.IntegerField()

    class Meta:
        unique_together = ("contestid", "problemid")


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)


class ProblemTag(models.Model):
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    tagid = models.ForeignKey(Tag, on_delete=models.PROTECT)


class Registration(models.Model):
    userid = models.ForeignKey(BSUser, on_delete=models.PROTECT)
    contestid = models.ForeignKey(Contest, on_delete=models.PROTECT)
    regtime = models.DateTimeField()
    starttime = models.DateTimeField(null=True)
    currentnumber = models.IntegerField(default=0)
    currenttime = models.DateTimeField(null=True)
    correct = models.IntegerField(null=True)
    timecost = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    rank = models.IntegerField(null=True)
    beforerating = models.IntegerField(null=True)
    afterrating = models.IntegerField(null=True)

    class Meta:
        unique_together = ("userid", "contestid")


class Record(models.Model):
    userid = models.ForeignKey(BSUser, on_delete=models.PROTECT)
    contestid = models.ForeignKey(Contest, on_delete=models.PROTECT)
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT)
    result = models.CharField(max_length=10, choices=[("正确", "正确"), ("错误", "错误")])
    submitted = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("userid", "contestid", "problemid")
