from django.db import models
from models.bsuser import BSUser
from models.contest import Contest


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
