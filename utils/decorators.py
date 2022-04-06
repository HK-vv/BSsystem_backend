import json
import traceback
from functools import wraps

from utils.auxilary import msg_response


def get_data(request):
    if request.method == 'GET':
        return request.params
    return json.loads(request.body)


def require_nothing():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            try:
                return func(request, get_data(request), *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                print(e.args)
                return msg_response(3)

        return inner

    return decorator


def require_admin_login():
    def decorator(func):
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

    return decorator


def require_super_login():
    def decorator(func):
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

    return decorator
