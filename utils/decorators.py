import traceback
from functools import wraps
from utils.auxilary import msg_response, get_data, session_expired


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


def need_user_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        try:
            request.params = get_data(request)
            return func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner


def require_user_login(func):
    @wraps(func)
    def inner(request, *args, **kwargs):
        if session_expired(request, 'openid'):
            return msg_response(2)
        try:
            request.params = get_data(request)
            return func(request, *args, **kwargs)
        except Exception as e:
            traceback.print_exc()
            print(e.args)
            return msg_response(3)

    return inner
