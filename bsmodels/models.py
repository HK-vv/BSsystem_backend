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
    is_superuser = models.BooleanField(default=False, choices=((False, 'admin'), (True, 'super')))

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
    authorid = models.ForeignKey(BSAdmin, on_delete=models.SET_NULL, blank=True, null=True)
    # tags = models.ManyToManyField(Tag, through=ProblemTag)

    # 选择题
    def __choice_check(self, answer, ur_answer):
        # 删除空格、分隔答案
        # ans = answer.replace(" ", "").split(',')
        # ur_ans = ur_answer.replace(" ", "").split(',')
        ans = list(answer.replace(" ", ""))
        ur_ans = list(ur_answer.replace(" ", ""))

        # 删除空白项
        while '' in ans:
            ans.remove('')
        while '' in ur_ans:
            ur_ans.remove('')

        # 长度不同则错
        if len(ans) != len(ur_ans):
            return 0
        for choice in ans:
            # 答案不在答题者答案中则错
            if choice not in ur_ans:
                return 0
        return 1

    # 填空题
    def __completion_check(self, answer, ur_answer):
        # 删除空格、分隔答案
        ans_temp = answer.replace(" ", "").split(',')
        ur_ans = ur_answer.replace(" ", "").split(',')

        # 删除空白项
        while '' in ans_temp:
            ans_temp.remove('')
        while '' in ur_ans:
            ur_ans.remove('')

        ans = []
        for word in ans_temp:
            ans.append(word.split('/'))

        # 长度不同则错
        if len(ans) != len(ur_ans):
            return 0

        length = len(ans)
        for i in range(0, length):
            ur_word = ur_ans[i]
            ans_word = ans[i]
            # 答案不在答题者答案中则错
            if ur_word not in ans_word:
                print(ur_word, ans_word)
                return 0
        return 1

    # 检查题目是否正确
    def iscorrect(self, ur_answer):
        answer = self.answer
        type = self.type

        # 单选、多选、判断
        if type in ['single', 'multiple', 'binary']:
            correct = self.__choice_check(answer, ur_answer)
        # 填空
        else:
            correct = self.__completion_check(answer, ur_answer)
        return correct


class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    start = models.DateTimeField()
    latest = models.DateTimeField()
    password = models.CharField(max_length=30, null=True)
    rated = models.BooleanField()
    authorid = models.ForeignKey(BSAdmin, on_delete=models.SET_NULL, blank=True, null=True)
    # problems = models.ManyToManyField(Problem, through=ContestProblem)


class ContestProblem(models.Model):
    contestid = models.ForeignKey(Contest, on_delete=models.SET_NULL, blank=True, null=True)
    problemid = models.ForeignKey(Problem, on_delete=models.SET_NULL, blank=True, null=True)
    number = models.IntegerField()
    duration = models.IntegerField()

    class Meta:
        unique_together = ("contestid", "problemid")


class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, unique=True)


class ProblemTag(models.Model):
    problemid = models.ForeignKey(Problem, on_delete=models.CASCADE, blank=True, null=True)
    tagid = models.ForeignKey(Tag, on_delete=models.CASCADE, blank=True, null=True)


class Registration(models.Model):
    userid = models.ForeignKey(BSUser, on_delete=models.SET_NULL, blank=True, null=True)
    contestid = models.ForeignKey(Contest, on_delete=models.SET_NULL, blank=True, null=True)
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
    userid = models.ForeignKey(BSUser, on_delete=models.SET_NULL, blank=True, null=True)
    contestid = models.ForeignKey(Contest, on_delete=models.SET_NULL, blank=True, null=True)
    problemid = models.ForeignKey(Problem, on_delete=models.SET_NULL, blank=True, null=True)
    result = models.CharField(max_length=10, choices=[("正确", "正确"), ("错误", "错误")])
    submitted = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("userid", "contestid", "problemid")
