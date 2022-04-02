from utils.auxilary import *
from models.models import *


def collect_problem(request):
    pass


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


def check(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(2)

    openid = request.session['openid']

    # newdata = request.params['newdata']
    # try:
    #     user = BSUser.objects.get(openid=openid)
    #     if 'username' in newdata:
    #         user.username = newdata['username']
    #     user.save()
    #     return msg_response(0)
    #
    # except BSUser.DoesNotExist:
    #     return msg_response(1, msg='用户不存在')
