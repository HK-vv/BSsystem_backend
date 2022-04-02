from utils.handler import *
from utils.auxilary import *
from models.models import *


def get_profile(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(ret=2, msg="登录过期")

    openid = request.session['openid']

    try:
        user = BSUser.objects.get(openid=openid)
        info = {
            'username': user.username,
            'rating': user.rating
        }
        return JsonResponse({'ret': 0,
                             'info': info})
    except BSUser.DoesNotExist:
        return msg_response(1, msg='用户不存在')


def modify_profile(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(ret=2, msg="登录过期")

    openid = request.session['openid']

    if 'newdata' not in request.params:
        return msg_response(3, msg='参数错误')

    newdata = request.params['newdata']
    try:
        user = BSUser.objects.get(openid=openid)
        if 'username' in newdata:
            user.username = newdata['username']
        user.save()
        return msg_response(0)

    except BSUser.DoesNotExist:
        return msg_response(1, msg='用户不存在')


method2handler = {
    'GET': get_profile,
    'POST': modify_profile
}


def profile(request):
    return dispatcher_base(request, method2handler)
