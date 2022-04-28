import datetime
import traceback

import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import Max, Avg, Min

from brainstorm.settings import OUTPUT_LOG, UPDATE_INTERVAL
from utils.auxilary import get_current_time


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
    A = models.CharField(max_length=50, null=True, blank=True)
    B = models.CharField(max_length=50, null=True, blank=True)
    C = models.CharField(max_length=50, null=True, blank=True)
    D = models.CharField(max_length=50, null=True, blank=True)
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
        ur_ans = ur_answer.replace(" ", "").replace("，", ",").split(',')

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

    def get_options(self):
        if self.type == 'single':
            options = [self.A, self.B, self.C, self.D]
        # 多选
        elif self.type == 'multiple':
            options = [self.A, self.B, self.C, self.D]
        # 判断
        elif self.type == 'binary':
            options = [self.A, self.B]
        # 填空
        else:
            options = []
        return options


class Contest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30, unique=True)
    start = models.DateTimeField()
    latest = models.DateTimeField()
    end = models.DateTimeField(null=True)
    password = models.CharField(max_length=30, null=True)
    rated = models.BooleanField()
    announced = models.BooleanField(default=False)
    ordered = models.BooleanField(default=False)
    updatetime = models.DateTimeField(default=pytz.UTC.localize(
        datetime.datetime.strptime("2022-1-1 00:00:00", '%Y-%m-%d %H:%M:%S')))
    authorid = models.ForeignKey(BSAdmin, on_delete=models.SET_NULL, blank=True, null=True)
    # problems = models.ManyToManyField(Problem, through=ContestProblem)

    def get_end_time(self):
        problems = ContestProblem.objects.filter(contestid=self.id)
        max_time = 0
        for problem in problems:
            max_time += problem.duration

        return self.latest + datetime.timedelta(seconds=max_time)

    def get_status(self):
        cur = pytz.UTC.localize(datetime.datetime.now())
        if cur < self.start:
            return 'upcoming'
        elif cur < self.end:
            return 'running'
        elif self.announced:
            return 'finished'
        else:
            return 'shut'

    def get_problems(self):
        ps = ContestProblem.objects.filter(contestid=self) \
            .order_by('number')
        ps = list(ps.values('number', 'problemid', 'duration'))
        ret = {}
        for x in ps:
            ret[x['number']] = {'id': x['problemid'], 'dt': x['duration']}
        return ret

    def count_problem(self):
        return ContestProblem.objects.filter(contestid=self).count()

    def update_leaderboard(self):
        cur = pytz.UTC.localize(datetime.datetime.now())
        if self.announced or cur < self.updatetime + datetime.timedelta(seconds=UPDATE_INTERVAL):
            return
        regs = Registration.objects.filter(contestid=self).order_by('-score', 'timecost')
        try:
            with transaction.atomic():
                for i in range(0, len(regs)):
                    if i == 0:
                        regs[i].rank = 1
                    else:
                        if regs[i].score == regs[i - 1].score and regs[i].timecost == regs[i - 1].timecost:
                            regs[i].rank = regs[i - 1].rank
                        else:
                            regs[i].rank = i + 1
                    regs[i].save()
                self.updatetime = max(cur, self.start)
                self.save()
                if OUTPUT_LOG:
                    print(f'比赛{self.id}排行榜已更新')
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            if OUTPUT_LOG:
                print(f'比赛{self.id}排行榜更新失败')

    def get_leaderboard(self, keyword=None):
        self.update_leaderboard()
        regs = Registration.objects.filter(contestid=self).order_by('rank')\
            .values('userid_id', 'score', 'timecost', 'correct', 'beforerating', 'afterrating', 'rank')
        if keyword:
            regs = regs.filter(userid__username__contains=keyword)

        regs = list(regs)
        for item in regs:
            item['changed_rating'] = item['afterrating'] - item['beforerating']
            item['before_rating'] = item['beforerating']
            del item['beforerating']
            del item['afterrating']

            item['username'] = BSUser.objects.get(openid=item['userid_id']).username
            del item['userid_id']
        return regs

    def get_user_rank(self, username):
        try:
            self.update_leaderboard()
            regs = Registration.objects.select_related('userid').filter(contestid=self, userid__username=username)\
                .values('score', 'timecost', 'correct', 'beforerating', 'afterrating', 'rank')[0]
            regs['changed_rating'] = regs['afterrating'] - regs['beforerating']
            regs['before_rating'] = regs['beforerating']
            del regs['beforerating']
            del regs['afterrating']
            regs['username'] = username
            return regs
        except:
            return None

    def get_score(self):
        regs = Registration.objects.filter(contestid=self)
        score = {
            'highest': regs.aggregate(Max('score'))['score__max'],
            'average': regs.aggregate(Avg('score'))['score__avg'],
            'lowest': regs.aggregate(Min('score'))['score__min'],
        }
        return score


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
    userid = models.ForeignKey(BSUser, on_delete=models.CASCADE, blank=True, null=True)
    contestid = models.ForeignKey(Contest, on_delete=models.CASCADE, blank=True, null=True)
    regtime = models.DateTimeField()
    starttime = models.DateTimeField(null=True)
    currentnumber = models.IntegerField(default=0)
    currenttime = models.DateTimeField(null=True)
    correct = models.IntegerField(null=True)
    timecost = models.IntegerField(null=True)
    score = models.IntegerField(null=True)
    rank = models.IntegerField(null=True, default=1)
    beforerating = models.IntegerField(null=True)
    afterrating = models.IntegerField(null=True)

    class Meta:
        unique_together = ("userid", "contestid")

    def start(self):
        with transaction.atomic():
            contest = self.contestid
            cur = get_current_time()
            if not contest.start <= cur <= contest.latest:
                raise Exception("Not in time window")
            if self.starttime is None:
                self.starttime = cur
                self.currenttime = cur
                self.currentnumber = 1
                self.save()

    def next_problem(self):
        """
            Note that this function only moves pointers.
            It does not return the problem object. Use `get_current_problem()` instead.
        """
        contest = self.contestid
        nc = self.currentnumber
        tc = self.currenttime
        ps = contest.get_problems()
        totn = len(ps)

        if nc > totn:
            return
        t = get_current_time()
        sm = datetime.timedelta(seconds=0)
        k = nc
        while k <= totn:
            if sm <= t - tc < sm + datetime.timedelta(seconds=ps[k]['dt']):
                break
            sm += datetime.timedelta(seconds=ps[k]['dt'])
            k += 1
        tar = max(k, nc + 1)
        if tar <= totn:
            sm = datetime.timedelta(seconds=0)
            for k in range(nc, tar + 1):
                sm += datetime.timedelta(seconds=ps[k]['dt'])
            tardt = min(sm - (t - tc), ps[tar]['dt'])
            assert tardt > datetime.timedelta(seconds=0)

            # update two pointers at the same time
            self.currentnumber = tar
            self.currenttime = t - (ps[k]['dt'] - tardt)
        else:
            self.currentnumber = totn + 1
            self.currenttime = t
        self.save()

    def submit_current(self, ans, check_pn=None):
        nc = self.currentnumber
        tc = self.currenttime
        contest = self.contestid
        ps = contest.get_problems()
        t = get_current_time()

        if check_pn and check_pn != nc:
            raise Exception("wrong problem to answer")
        if t - tc > datetime.timedelta(seconds=ps[nc]['dt']):
            if OUTPUT_LOG:
                print(f"timeout on {nc}th problem ")
            return "timeout"

        Record.create(reg=self, pno=nc, ans=ans).save()

    def get_current_problem(self):
        totn = Contest.objects.get(contestid=self).count_problem()
        t = get_current_time()
        if 0 < self.currentnumber <= totn:
            ct = ContestProblem.objects.get(contestid=self, number=self.currentnumber)
            return ct.problemid, self.currentnumber, (ct.duration - (t - self.currenttime)).total_seconds()


class Record(models.Model):
    userid = models.ForeignKey(BSUser, on_delete=models.SET_NULL, blank=True, null=True)
    contestid = models.ForeignKey(Contest, on_delete=models.SET_NULL, blank=True, null=True)
    problemid = models.ForeignKey(Problem, on_delete=models.SET_NULL, blank=True, null=True)
    result = models.CharField(max_length=10, choices=[("T", "right"), ("F", "wrong")])
    submitted = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("userid", "contestid", "problemid")

    @classmethod
    def create(cls, reg, pno, ans):
        rec = cls(userid=reg.userid,
                  contestid=reg.contestid,
                  problemid=ContestProblem.objects.get(contestid=reg.contestid, number=pno).problemid,
                  submitted=ans)
        res = rec.problemid.iscorrect(ans)
        rec.result = 'T' if res else 'F'
        return rec

