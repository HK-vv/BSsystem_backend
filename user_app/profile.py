from utils.auxilary import *
from utils.handler import *
from bsmodels.models import BSUser
from utils.decorators import *


@require_user_login()
def get_profile(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(ret=2)

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


@require_user_login()
def modify_profile(request):
    # 检测是否登录过期
    if session_expired(request, 'openid'):
        return msg_response(2)

    openid = request.session['openid']

    if 'newdata' not in request.params:
        return msg_response(3)

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
