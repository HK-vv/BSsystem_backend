from django.db.models import Q

from brainstorm.settings import OUTPUT_LOG
from utils.auxiliary import *
from utils.decorators import *
from bsmodels.models import Tag, BSUser, Problem
from bsmodels.models import ProblemTag
import random

MAX_PROBLEM_AMOUNT = 50


def split_tag(tag):
    return tag.split(' ')


@require_user_login
def collect_problem(request, data):
    tag = data['tag']
    amount = int(data['amount'])
    tag = split_tag(tag)

    try:
        tags = Tag.objects.filter(name__in=tag)
        tagsid = tags.values('id')

        allproblemsid = list(ProblemTag.objects.filter(tagid__in=tagsid).
                             values_list('problemid', flat=True).distinct())

        problemsid = Problem.objects.filter(Q(id__in=allproblemsid) & Q(public=True)).values_list('id', flat=True)
        problemsid = list(problemsid)

        # 题目数量不能超过最大题数
        total = min(amount, len(problemsid), MAX_PROBLEM_AMOUNT)

        # 随机选题
        problems = random.sample(problemsid, total)

        if OUTPUT_LOG:
            user = BSUser.objects.get(openid=request.session['openid'])
            print(f"{user.username} 开始了练习")

        return JsonResponse({'ret': 0,
                             'problems': problems,
                             'total': total})

    except Tag.DoesNotExist:
        return msg_response(1, msg='标签不存在')


@require_user_login
def get_problem(request, data):
    pid = data['id']

    try:
        problem = Problem.objects.get(id=pid)
        # 题目不公开
        if not problem.public:
            return msg_response(1, msg='题目未公开')
        typ = problem.type
        options = problem.get_options()

        if OUTPUT_LOG:
            user = BSUser.objects.get(openid=request.session['openid'])
            print(f"{user.username} 正在练习第 {pid} 题")

        return JsonResponse({'ret': 0,
                             'type': typ,
                             'description': problem.description,
                             'options': options
                             })

    # 题目不存在
    except Problem.DoesNotExist:
        return msg_response(1, msg='题目不存在')


@require_user_login
def check(request, data):
    problem_id = data['problem_id']
    ur_answer = data['user_answer']

    try:
        problem = Problem.objects.get(id=problem_id)
        if not problem.public:
            msg_response(1, msg='题目未公开')

        return JsonResponse({'ret': 0,
                             'correct': problem.iscorrect(ur_answer),
                             'answer': problem.answer})

    except Problem.DoesNotExist:
        return msg_response(1, msg='题目不存在')
