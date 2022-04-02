from django.http import JsonResponse
from django.contrib.auth import authenticate
import json
import requests


def login(request):
    code = json.loads(request.body)
    if "code" not in code:
        return JsonResponse({'ret': 3, 'msg': '参数有误'})

    code = code['code']
    print(code)

    response = requests.get(f'https://api.weixin.qq.com/sns/jscode2session?appid={APPID}&secret={SECRET}&js_code={code}'
                            '&grant_type=authorization_code')

    info = response.json()
    print(info)
    if 'errcode' in info:
        return JsonResponse({'ret': info['errcode'], 'msg': info['errmsg']})
    openid = info['openid']
    session_key = info['session_key']

    request.session['openid'] = openid
    request.session['session_key'] = session_key

    return JsonResponse({'ret': 0,
                         'username': 'name'})


def logout(request):
    print("logout...")
    # 使用登出方法
    print(request.COOKIES)
    if 'sessionid' not in request.COOKIES:
        return JsonResponse({'ret': 2, 'msg': '登录过期'})

    del request.session['openid']
    del request.session['session_key']
    return JsonResponse({'ret': 0})
