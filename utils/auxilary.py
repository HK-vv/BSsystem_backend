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


# Here's an example of applying this function in serialization
# Let ori=[{'mydata':1},{'mydata':2},{'mydata':345}],
# and mp={'mydata': "my_data"}
# Then we return this: [{'my_data':1},{'my_data':2},{'my_data':345}]
#
# Notice: It would lead to UB if `mp` is overlap.
def dict_list_decorator(ori: list, mp: dict) -> list:
    for x in ori:
        for a, b in mp:
            x[b] = x.pop(a)
    return ori


def get_ip_address(request):
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if not ip:
        ip = request.META.get('REMOTE_ADDR', "")
    client_ip = ip.split(",")[-1].strip() if ip else ""
    return client_ip