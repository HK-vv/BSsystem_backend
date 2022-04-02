import string
import json
import requests
import random
from brainstorm.settings import APPID
from brainstorm.settings import SECRET
from models.models import *
from utils.auxilary import *


# 登陆
def login(request):
    code = json.loads(request.body)
    if "code" not in code:
        return JsonResponse({'ret': 3, 'msg': '参数有误'})

    code = code['code']
    # print(code)

    # response = requests.get(f'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={code}'
    #                         '&grant_type=authorization_code')
    #
    # info = response.json()
    # # print(info)
    # if 'errcode' in info:
    #     return JsonResponse({'ret': info['errcode'], 'msg': info['errmsg']})
    #
    # openid = info['openid']
    # session_key = info['session_key']
    openid = code
    user = BSUser.objects.filter(openid=openid)
    # 不存在用户，注册
    if not user:
        username = "bs_" + ''.join(random.sample(string.ascii_letters + string.digits, 10))
        while BSUser.objects.filter(username=username):
            username = "bs_" + ''.join(random.sample(string.ascii_letters + string.digits, 10))

        BSUser.objects.create(openid=openid,
                              username=username)
        print(username + " 用户成功注册")
    else:
        username = user[0].username

    print(username + " 用户已登录")

    # 设置session
    request.session['openid'] = openid
    # request.session['session_key'] = session_key

    return JsonResponse({'ret': 0,
                         'username': username})


def logout(request):
    # 使用登出方法
    if session_expired(request, 'openid'):
        return msg_response(ret=2, msg="登录过期")
    openid = request.session['openid']
    username = BSUser.objects.get(openid=openid).username
    print(username + " 用户已登出")
    del request.session['openid']
    # del request.session['session_key']
    return JsonResponse({'ret': 0})
