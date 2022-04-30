import datetime
import json
import re

import pytz
from django.http import JsonResponse
import requests

from brainstorm.settings import OUTPUT_LOG


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
        for a, b in mp.values():
            x[b] = x.pop(a)
    return ori


def get_current_time():
    return pytz.UTC.localize(datetime.datetime.now())


def get_ip(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if not ip:
        ip = request.META.get('REMOTE_ADDR', 'retrieve IP failed')
    return ip


def output_ip_info(request):
    ip = get_ip(request)
    print(f"Request received from {ip}")

    # It seems API below is not stable enough...
    #
    # url = "https://www.ip138.com/iplookup.asp?ip={}&action=2".format(ip)
    #
    # headers = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.100 Safari/537.36'
    # }
    #
    # response = requests.get(url=url, headers=headers)
    # response.encoding = 'gb2312'
    #
    # for match in re.finditer('"(ASN归属地|yunyin|idc|prov|city|ct)":"(.*?)"', response.text):
    #     print(match.group(), end=', ')
    # print()


def output_request_info(request):
    output_ip_info(request)
