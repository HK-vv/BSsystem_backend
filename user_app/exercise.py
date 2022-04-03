from utils.auxilary import *
from models.models import *
import random


def split_tag(tag):
    return tag.split(' ')


def collect_problem(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(2)

    request.params = request.GET
    if 'tag' not in request.params or 'amount' not in request.params:
        return msg_response(3)

    tag = request.params['tag']
    amount = int(request.params['amount'])
    tag = split_tag(tag)

    try:
        tags = Tag.objects.filter(name__in=tag)
        tagsid = tags.values('id')

        problemsid = ProblemTag.objects.filter(tagid__in=tagsid).values_list('problemid', flat=True).distinct()
        problemsid = list(problemsid)

        # 题目数量不能超过最大题数
        total = min(amount, len(problemsid))

        # 随机选题
        problems = random.sample(problemsid, total)

        return JsonResponse({'ret': 0,
                             'problems': problems,
                             'total': total})

    except Tag.DoesNotExist:
        return msg_response(1, msg='标签不存在')


def get_problem(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(2)

    request.params = request.GET
    if 'id' not in request.params:
        return msg_response(3)
    id = request.params['id']

    try:
        problem = Problem.objects.get(id=id)
        # 题目不公开
        if not problem.public:
            return msg_response(1, msg='题目未公开')
        type = problem.type
        # 单选
        if type == 'single':
            options = [problem.A, problem.B, problem.C, problem.D]
        # 多选
        elif type == 'multiple':
            options = [problem.A, problem.B, problem.C, problem.D]
        # 判断
        elif type == 'binary':
            options = [problem.A, problem.B]
        # 填空
        else:
            options = []

        return JsonResponse({'ret': 0,
                             'type': type,
                             'description': problem.description,
                             'options': options
                             })

    # 题目不存在
    except Problem.DoesNotExist:
        return msg_response(1, msg='题目不存在')


# 选择题
def choice_check(answer, ur_answer):
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


def completion_check(answer, ur_answer):
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


def check(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(2)

    request.params = request.GET
    if 'problem_id' not in request.params or 'answer' not in request.params:
        return msg_response(3)

    problem_id = request.params['problem_id']
    ur_answer = request.params['answer']

    try:
        problem = Problem.objects.get(id=problem_id)
        answer = problem.answer
        type = problem.type

        # 单选、多选、判断
        if type in ['single', 'multiple', 'binary']:
            correct = choice_check(answer, ur_answer)
        # 填空
        else:
            correct = completion_check(answer, ur_answer)
        return JsonResponse({'ret': 0,
                             'correct': correct,
                             'answer': answer})

    except Problem.DoesNotExist:
        return msg_response(1, msg='题目不存在')
