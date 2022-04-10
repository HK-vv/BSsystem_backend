import json
from django.http import JsonResponse
from bsmodels.models import Problem


def get_data(request):
    if request.FILES:
        return request.POST
    if request.method in ('GET', 'DELETE'):
        return request.GET
    if request.body:
        return json.loads(request.body)
    return None


def ret_response(ret, dic=None):
    if dic is None:
        dic = {}
    return JsonResponse({**{'ret': ret}, **dic})


def msg_response(ret, msg=None):
    if ret == 2:
        return ret_response(ret, {'msg': "登陆过期"})
    if ret == 3:
        return ret_response(ret, {'msg': "其他错误"})
    if msg is None:
        return ret_response(ret)
    return ret_response(ret, {'msg': msg})


def session_expired(request, keyword):
    if 'sessionid' not in request.COOKIES or keyword not in request.session:
        return True
    else:
        return False
