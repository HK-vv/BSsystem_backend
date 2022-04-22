from datetime import *
import random

import pytz
from django.db import transaction, IntegrityError

from brainstorm.settings import OUTPUT_LOG
from bsmodels.models import Contest, Problem, ContestProblem
from utils.auxilary import ret_response
from utils.decorators import *
from utils.handler import dispatcher_base


def data2contest(data, user):
    name = data['name']
    try:
        start = pytz.UTC.localize(datetime.strptime(data['start'], '%Y-%m-%d %H:%M:%S'))
        latest = pytz.UTC.localize(datetime.strptime(data['latest'], '%Y-%m-%d %H:%M:%S'))
    except Exception as e:
        raise Exception('时间格式错误')

    if start > latest:
        raise Exception('比赛开始时间不能晚于最晚进入时间')

    password = data.get('password')
    password = None if password == "" else password
    rated = data['rated']
    ordered = data['ordered']

    contest = Contest(name=name,
                      start=start,
                      latest=latest,
                      password=password,
                      rated=rated,
                      ordered=ordered,
                      authorid=user)
    return contest


def contest_dispatcher(request):
    method2handler = {
        'GET': get_contest,
        'POST': modify_contest,
        'PUT': add_contest
    }
    return dispatcher_base(request, method2handler)


@require_admin_login
def get_contest(request, data):
    contestid = data['contestid']
    try:
        contest = Contest.objects.get(id=contestid)

        info = {'contestid': contest.id,
                'name': contest.name,
                'start': contest.start.strftime('%Y-%m-%d %H:%M:%S'),
                'latest': contest.latest.strftime('%Y-%m-%d %H:%M:%S'),
                'password': contest.password,
                'rated': contest.rated,
                'ordered': contest.ordered,
                'time_limited': {
                    "single": 0,
                    "multiple": 0,
                    "binary": 0,
                    "completion": 0
                },
                'author': contest.authorid.username}

        contest_problem = ContestProblem.objects.filter(contestid=contest)\
            .exclude(problemid__isnull=True).order_by('number')
        problems = list(contest_problem.values('problemid', 'duration'))
        # print(problems)

        problemsid = []

        for item in problems:
            problemid = item['problemid']
            if Problem.objects.filter(id=problemid).exists():
                problem = Problem.objects.get(id=problemid)
                info['time_limited'][problem.type] = item['duration']
            problemsid.append(problemid)

        info['problems'] = problemsid

        return ret_response(0, {'info': info})

    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, f'比赛{contestid}不存在')


@require_admin_login
def modify_contest(request, data):
    user = request.user
    contestid = data['contestid']
    newdata = data['newdata']

    contest = Contest.objects.get(id=contestid)

    if contest.authorid != user and not user.is_superuser:
        return msg_response(1, "权限不足")

    try:
        nt = data2contest(newdata, contest.authorid)
        nt.id = contest.id
    except Exception as e:
        return msg_response(1, e.args)

    _time = newdata['time_limited']
    problems = newdata['problems']

    try:
        nt.save()

        ContestProblem.objects.filter(contestid_id=contestid).delete()

        if not contest.ordered:
            random.shuffle(problems)

        no = 1
        for problemid in problems:
            problem = Problem.objects.get(id=problemid)
            if not problem:
                raise Exception(f"题目{problemid}不存在")

            ContestProblem.objects.create(problemid=problem,
                                          contestid=contest,
                                          duration=_time[problem.type],
                                          number=no)
            no = no + 1
        nt.end = nt.get_end_time()
        nt.save()
    except Exception as e:
        return msg_response(1, e.args)

    if OUTPUT_LOG:
        print(f"{user.username} 修改了比赛 {contestid}")

    return msg_response(0)


@require_admin_login
def add_contest(request, data):
    user = request.user
    try:
        contest = data2contest(data, user)
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, e.args)

    problems = data['problems']
    _time = data['time_limited']

    try:
        with transaction.atomic():
            contest.save()

            if not contest.ordered:
                random.shuffle(problems)

            no = 1
            for problemid in problems:
                problem = Problem.objects.get(id=problemid)
                if not problem:
                    raise Exception(f"题目{problemid}不存在")

                ContestProblem.objects.create(problemid=problem,
                                              contestid=contest,
                                              duration=_time[problem.type],
                                              number=no)
                no = no + 1
            contest.end = contest.get_end_time()
            contest.save()
    except IntegrityError as ie:
        traceback.print_exc()
        print(ie.args)
        return msg_response(1, '比赛名已存在')
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, e.args)

    if OUTPUT_LOG:
        print(f"{user.username} 创建了比赛 {contest.id}")

    return msg_response(0)


@require_admin_login
def del_contest(request, data):
    contests = data['contests']
    user = request.user
    try:
        with transaction.atomic():
            for id in contests:
                contest = Contest.objects.get(id=id)
                if contest.authorid != user and not user.is_superuser:
                    return msg_response(1, f'比赛{id}不是您创建的比赛')
                contest.delete()
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, f'比赛{id}不存在')

    if OUTPUT_LOG:
        print(f"{user.username} 删除了比赛 {str(contests)}")

    return msg_response(0)
