import traceback
from functools import wraps

from utils.auxilary import msg_response


def require_admin_login():
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return msg_response(2)
            try:
                return func(request, *args, **kwargs)
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
            if not request.user.is_authenticated():
                return msg_response(2)
            if not request.user.is_superuser():
                return msg_response(1, "权限不足")
            try:
                return func(request, *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                print(e.args)
                return msg_response(3)

        return inner

    return decorator
