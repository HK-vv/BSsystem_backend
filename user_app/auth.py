import string
import requests
import random
from brainstorm.settings import APPID, OUTPUT_LOG
from brainstorm.settings import SECRET
from utils.decorators import *
from utils.auxiliary import *
from bsmodels.models import BSUser

DEBUG = False


# 登陆
@require_nothing
def login(request, data):
    code = data['code']

    if DEBUG:
        openid = code
        session_key = code

    else:
        response = requests.get(f'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={code}'
                                '&grant_type=authorization_code')

        info = response.json()

        if 'errcode' in info:
            return JsonResponse({'ret': info['errcode'], 'msg': info['errmsg']})

        openid = info['openid']
        session_key = info['session_key']

    user = BSUser.objects.filter(openid=openid)
    # 不存在用户，注册
    if not user:
        username = "bs_" + ''.join(random.sample(string.ascii_letters + string.digits, 10))
        while BSUser.objects.filter(username=username):
            username = "bs_" + ''.join(random.sample(string.ascii_letters + string.digits, 10))

        BSUser.objects.create(openid=openid,
                              username=username).set_initial_rank()
        if OUTPUT_LOG:
            print(f"{username} 用户成功注册")
    else:
        username = user[0].username

    if OUTPUT_LOG:
        print(f"{username} 用户上线了！")

    # 设置session
    request.session['openid'] = openid
    request.session['session_key'] = session_key

    return JsonResponse({'ret': 0,
                         'username': username})


@require_user_login
def logout(request, data):
    # 使用登出方法
    openid = request.session['openid']
    username = BSUser.objects.get(openid=openid).username
    if OUTPUT_LOG:
        print(f"{username} 用户已登出")
    del request.session['openid']
    del request.session['session_key']
    return JsonResponse({'ret': 0})
