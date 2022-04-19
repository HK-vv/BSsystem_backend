import json

from django.contrib.auth import login, authenticate, logout

from brainstorm.settings import OUTPUT_LOG
from bsmodels.models import BSAdmin
from utils.auxilary import msg_response
from utils.decorators import *


@require_nothing
def log_in(request, data):
    usn = data['username']
    pwd = data['password']

    user = authenticate(username=usn, password=pwd)
    if user is None:
        return msg_response(1, "用户名或密码错误")
    login(request, user)
    if OUTPUT_LOG:
        print(f"{usn} 上线了！")
    return msg_response(0)


@require_admin_login
def log_out(request, data):
    if request.user.is_authenticated:
        logout(request)

    if OUTPUT_LOG:
        print(f"{request.user.username} 下线了！")

    return msg_response(0)
