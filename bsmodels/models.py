import datetime
from datetime import timedelta
import traceback
from math import exp, sqrt

import pytz
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models import Max, Avg, Min

from brainstorm.settings import OUTPUT_LOG, UPDATE_INTERVAL
from utils.auxiliary import get_current_time
from utils.exceptions import SubmitWrongProblemError, ContestFinishedError


class BSUser(models.Model):
    openid = models.CharField(max_length=40, primary_key=True)
    username = models.CharField(max_length=40, unique=True)
    rating = models.IntegerField(default=0)
    rank = models.IntegerField(default=0)

    def set_initial_rank(self):
        self.rank = BSUser.objects.filter(rating__gt=0).count() + 1
        self.save()


class BSAdmin(AbstractUser):
    DEFAULT_PASSWORD = '123456'

    username = models.CharField(max_length=40, unique=True)
    password = models.CharField(max_length=40, default=DEFAULT_PASSWORD)
    email = models.CharField(max_length=40, null=True)
    phone = models.CharField(max_length=40, null=True)
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
    name = models.CharField(max_length=40)
    start = models.DateTimeField()
    latest = models.DateTimeField()
    end = models.DateTimeField(null=True)
    password = models.CharField(max_length=40, null=True)
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

        return self.latest + timedelta(seconds=max_time)

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
        if self.announced or cur < self.updatetime + timedelta(seconds=UPDATE_INTERVAL):
            return
        regs = Registration.objects.filter(contestid=self).order_by('-score', 'timecost')
        try:
            with transaction.atomic():
                self.update_scores()
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
        regs = Registration.objects.filter(contestid=self).order_by('rank')
        if keyword:
            regs = regs.filter(userid__username__contains=keyword)

        items = []
        for reg in regs:
            user = reg.userid

            item = {
                'rank': reg.rank,
                'username': user.username,
                'score': reg.score,
                'correct': reg.correct_count(),
            }

            if reg.afterrating and reg.beforerating:
                item['changed_rating'] = reg.afterrating - reg.beforerating
                item['before_rating'] = reg.beforerating
            else:
                item['changed_rating'] = None
                item['before_rating'] = user.rating

            item['timecost'] = reg.timecost if reg.timecost else 0

            items.append(item)
        return items

    def get_user_rank(self, username):
        try:
            self.update_leaderboard()
            regs = Registration.objects.select_related('userid').filter(contestid=self, userid__username=username)

            reg = regs[0]
            user = reg.userid

            item = {
                'rank': reg.rank,
                'username': user.username,
                'score': reg.score,
                'correct': reg.correct_count(),
            }

            if reg.afterrating and reg.beforerating:
                item['changed_rating'] = reg.afterrating - reg.beforerating
                item['before_rating'] = reg.beforerating
            else:
                item['changed_rating'] = None
                item['before_rating'] = user.rating

                item['timecost'] = reg.timecost if reg.timecost else 0

            return item

        except Exception as e:
            traceback.print_exc()
            print(e.args)

    def get_score(self):
        regs = Registration.objects.filter(contestid=self)
        score = {
            'highest': regs.aggregate(Max('score'))['score__max'],
            'average': regs.aggregate(Avg('score'))['score__avg'],
            'lowest': regs.aggregate(Min('score'))['score__min'],
        }
        return score

    def annouce(self, rated):
        if self.announced:
            return
        if rated and not self.rated:
            raise Exception("could not rate the unrated contest")
        with transaction.atomic():
            if rated:
                self.__update_rating()
                update_rank()
            self.announced = True
            self.save()

    def __update_rating(self):
        self.update_leaderboard()
        regs = Registration.objects.filter(contestid=self)
        regs = list(regs)
        blst = {}
        rlst = {}
        for reg in regs:
            blst[reg.userid_id] = reg.userid.rating
            rlst[reg.userid_id] = reg.rank

        alst = blst  # TODO: call rating calculate function instead

        for reg in regs:
            reg.beforerating = blst[reg.userid_id]
            reg.afterrating = alst[reg.userid_id]
            reg.save()
            reg.userid.rating = reg.afterrating
            reg.userid.save()

    def update_scores(self):
        regs = Registration.objects.filter(contestid=self)
        with transaction.atomic():
            for r in regs:
                r.update_score()

    def statistics(self):
        prob = self.get_problems()
        regs = Registration.objects.filter(contestid=self)
        records = Record.objects.filter(registerid__in=regs)

        problems = []
        for pno in prob.keys():
            rec = records.filter(problemno=pno)

            item = {
                'problemno': pno,
                'correct': rec.filter(result='T').count(),
                'all': rec.count(),
            }
            problems.append(item)

        total = len(problems)

        max_score = 100
        min_score = 0
        sections = []

        for section in range(10):
            l = min_score + section * max_score / 10.0
            r = min_score + (section + 1) * max_score / 10.0
            if section == 0:
                sections.append(regs.filter(score__gte=l, score__lte=r).count())
            else:
                sections.append(regs.filter(score__gt=l, score__lte=r).count())

        return {
            'problems': problems,
            'total': total,
            'sections': sections,
            'average_score': self.get_score()['average'],
            'registrants': regs.count(),
            'participants': records.values('registerid').distinct().count(),
        }


class ContestProblem(models.Model):
    contestid = models.ForeignKey(Contest, on_delete=models.CASCADE, blank=True, null=True)
    problemid = models.ForeignKey(Problem, on_delete=models.PROTECT, blank=True, null=True)
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
    score = models.FloatField(null=True)
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
        sm = timedelta(seconds=0)
        k = nc
        while k <= totn:
            if sm <= t - tc < sm + timedelta(seconds=ps[k]['dt']):
                break
            sm += timedelta(seconds=ps[k]['dt'])
            k += 1
        tar = max(k, nc + 1)
        if tar <= totn:
            sm = timedelta(seconds=0)
            for k in range(nc, tar + 1):
                sm += timedelta(seconds=ps[k]['dt'])
            tardt = min(sm - (t - tc), timedelta(seconds=ps[tar]['dt']))
            assert tardt > timedelta(seconds=0)

            # update two pointers at the same time
            self.currentnumber = tar
            self.currenttime = t - (timedelta(seconds=ps[tar]['dt']) - tardt)
        else:
            self.currentnumber = totn + 1
            self.currenttime = t

        self.timecost = (self.currenttime - self.starttime).total_seconds()
        self.save()

    def submit_current(self, ans, check_pn=None):
        nc = self.currentnumber
        tc = self.currenttime
        contest = self.contestid
        ps = contest.get_problems()
        t = get_current_time()

        r = None
        if check_pn and check_pn != nc:
            raise SubmitWrongProblemError(f"submit {check_pn} to {nc}")
        if t - tc > timedelta(seconds=ps[nc]['dt']):
            Record.create(reg=self, pno=nc, ans='').save()
            r = "timeout"
            if OUTPUT_LOG:
                print(f"timeout on {nc}th problem ")
        else:
            Record.create(reg=self, pno=nc, ans=ans).save()
            r = "success"

        self.update_score()
        self.next_problem()

        return r

    def get_current_problem(self):
        totn = self.contestid.count_problem()
        t = get_current_time()
        if 0 < self.currentnumber <= totn:
            ct = ContestProblem.objects.get(contestid=self.contestid, number=self.currentnumber)
            return ct.problemid, self.currentnumber, \
                   (timedelta(seconds=ct.duration) - (t - self.currenttime)).total_seconds()
        else:
            raise ContestFinishedError("It's already finished")

    def get_answer_status(self, pno):
        try:
            rec = Record.objects.get(registerid=self, problemno=pno)
        except Record.DoesNotExist:
            rec = None
        pid = ContestProblem.objects.get(contestid=self.contestid, number=pno).problemid_id
        d = {}
        if rec:
            if rec.submitted == "":
                d.update({'status': 'timeout'})
            else:
                d.update({'status': 'valid',
                          'correct': rec.result == 'T',
                          'submitted': rec.submitted})
        else:
            d.update({'status': 'miss'})
        d.update({'pid': pid})
        return d

    def get_answer_statuses(self):
        tot = self.contestid.count_problem()
        lst = []
        for i in range(1, tot + 1):
            lst.append(self.get_answer_status(i))
        return lst

    def correct_count(self):
        return Record.objects.filter(registerid=self, result='T').count()

    def update_score(self):
        k = 1.56

        def f(x):
            return 100 * (1 - exp(-k * sqrt(x)))

        tot = self.contestid.count_problem()
        s = self.get_answer_statuses()
        p = tp = ts = 0
        i = 0
        for d in s:
            i += 1
            cp = ContestProblem.objects.get(number=i, contestid=self.contestid)
            ts += cp.duration
            if d['status'] == 'valid' and d['correct']:
                p += 1
                tp += cp.duration
        rp = p / tot
        t = self.timecost
        t = 0 if t is None else t
        t = max(t, ts / 10)
        s = 0
        if t != 0:
            s = rp ** 2 * tp / t
        self.score = f(s)
        self.save()
        if OUTPUT_LOG:
            print(f"score updated to {self.score}")


class Record(models.Model):
    registerid = models.ForeignKey(Registration, on_delete=models.CASCADE, null=True)
    problemno = models.IntegerField(null=True)
    result = models.CharField(max_length=10, choices=[("T", "right"), ("F", "wrong")])
    submitted = models.CharField(max_length=100, null=True)

    class Meta:
        unique_together = ("registerid", "problemno")

    @classmethod
    def create(cls, reg, pno, ans):
        rec = cls(registerid=reg,
                  problemno=pno,
                  submitted=ans)
        problem = Problem.objects.get(contestproblem__contestid=reg.contestid,
                                      contestproblem__number=pno)
        res = problem.iscorrect(ans)
        rec.result = 'T' if res else 'F'
        return rec

    def get_problem(self):
        return Problem.objects.get(contestproblem__contestid=self.registerid.contestid,
                                   contestproblem__number=self.problemno)


def update_rank():
    users = BSUser.objects.order_by('-rating')
    try:
        with transaction.atomic():
            for i in range(0, len(users)):
                if i == 0:
                    users[i].rank = 1
                else:
                    if users[i].rating == users[i - 1].rating:
                        users[i].rank = users[i - 1].rank
                    else:
                        users[i].rank = i + 1
                users[i].save()

            if OUTPUT_LOG:
                print(f'rating排行榜已更新')
    except Exception as e:
        if OUTPUT_LOG:
            print(f'rating排行榜更新失败')
        raise e
