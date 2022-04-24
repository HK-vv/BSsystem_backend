import traceback
from functools import wraps

from bsmodels.models import BSUser
from utils.auxilary import msg_response, get_data, session_expired, get_ip_address


def print_info(dec):
    @wraps(dec)
    def dec_level(func, *args, **kwargs):
        @wraps(func)
        def inner(request, *args, **kwargs):
            print(f"request from {get_ip_address(request)}")
            r = func(request, *args, **kwargs)
            print("---------------------------------------")
            return r

        return inner

    return dec_level


@print_info
def require_nothing(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        try:
            return func(request, get_data(request), *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner


@print_info
def require_admin_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return msg_response(2)
        try:
            return func(request, get_data(request), *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner


@print_info
def require_super_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return msg_response(2)
        if not request.user.is_superuser:
            return msg_response(1, "权限不足")
        try:
            return func(request, get_data(request), *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner


@print_info
def require_user_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if session_expired(request, 'openid'):
            return msg_response(2)
        try:
            request.user = BSUser.objects.get(id=request.session['openid'])
            return func(request, get_data(request), *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner
