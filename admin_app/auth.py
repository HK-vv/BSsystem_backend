import json

from django.contrib.auth import login, authenticate, logout

from models.bsadmin import BSAdmin
from utils.auxilary import msg_response


def log_in(request):
    data = json.loads(request.body)
    usn = data.get('username')
    pwd = data.get('password')
    print(usn, "is logging in")
    user = authenticate(username=usn, password=pwd)
    if user is None:
        return msg_response(1, "用户名或密码错误")
    login(request, user)
    return msg_response(0)


def log_out(request):
    if request.user.is_authenticated:
        logout(request)
    return msg_response(0)
