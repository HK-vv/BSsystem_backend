from django.http import JsonResponse


def msg_response(ret, msg=None):
    if ret == 2:
        return JsonResponse({'ret': ret,
                             'msg': '登录过期'})
    if ret == 3:
        return JsonResponse({'ret': ret,
                             'msg': '参数错误'})
    if msg is None:
        return JsonResponse({'ret': ret})
    return JsonResponse({'ret': ret, 'msg': msg})


def session_expired(request, keyword):
    if 'sessionid' not in request.COOKIES or keyword not in request.session:
        return True
    else:
        return False
