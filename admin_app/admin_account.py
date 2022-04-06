from django.db import DatabaseError
from django.http import JsonResponse

from bsmodels.models import BSAdmin
from utils.auxilary import msg_response, ret_response
from utils.decorators import require_admin_login, require_super_login


def root_dispatcher(request):
    if request.method == 'PUT':
        return create_account(request)
    if request.method == 'GET':
        return get_account(request)
    if request.method == 'POST':
        return modify_account(request)
    if request.method == 'DELETE':
        return modify_account(request)
    return msg_response(3)


@require_super_login()
def create_account(request, data):
    try:
        BSAdmin.objects.create(username=data['username']).save()
    except DatabaseError:
        return msg_response(1, "用户名已存在")
    return msg_response(0)


@require_admin_login()
def get_account(request, data):
    user = BSAdmin(request.user)
    info = {'username': user.username,
            'email': user.email,
            'phone': user.phone}
    return ret_response(0, {'info': info})


@require_admin_login()
def modify_account(request, data):
    pass


@require_super_login()
def delete_account(request, data):
    BSAdmin.objects.get(username=data['username']).delete()
    return msg_response(0)


@require_admin_login()
def account_list(request, data):
    pass


@require_admin_login()
def is_super(request, data):
    user = BSAdmin(request.user)
    return ret_response(0, {'issuper': user.is_superuser})


@require_super_login()
def reset_password(request, data):
    pass


@require_admin_login()
def integrity_verification(request, data):
    user = BSAdmin(request.user)
    integrity = user.email is not None and user.phone is not None
    return ret_response(0, {'integrity': integrity})
