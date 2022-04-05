from django.http import JsonResponse
from models.models import *


def msg_response(ret, msg=None):
    if ret == 2:
        return JsonResponse({'ret': ret,
                             'msg': '登录过期'})
    if ret == 3:
        return JsonResponse({'ret': ret,
                             'msg': '其他错误'})
    if msg is None:
        return JsonResponse({'ret': ret})
    return JsonResponse({'ret': ret, 'msg': msg})


def session_expired(request, keyword):
    if 'sessionid' not in request.COOKIES or keyword not in request.session:
        return True
    else:
        return False


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


# 填空题
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


# 检查题目是否正确
def iscorrect(problem_id, ur_answer):
    problem = Problem.objects.get(id=problem_id)
    answer = problem.answer
    type = problem.type

    # 单选、多选、判断
    if type in ['single', 'multiple', 'binary']:
        correct = choice_check(answer, ur_answer)
    # 填空
    else:
        correct = completion_check(answer, ur_answer)
    return correct
