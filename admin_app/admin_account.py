from django.core import serializers
from django.core.paginator import Paginator
from django.db import DatabaseError
from django.db.models.functions import Lower
from django.http import JsonResponse
from brainstorm.settings import OUTPUT_LOG
from bsmodels.models import BSAdmin
from utils.auxiliary import msg_response, ret_response
from utils.decorators import require_admin_login, require_super_login
from utils.handler import dispatcher_base


def root_dispatcher(request):
    method2handler = {
        'GET': get_account,
        'POST': modify_account,
        'PUT': create_account,
        'DELETE': delete_account
    }
    return dispatcher_base(request, method2handler)


@require_admin_login
def get_username(request, data):
    return ret_response(0, {'username': request.user.username})


@require_super_login
def create_account(request, data):
    try:
        BSAdmin.objects.create_user(username=data['username'],
                                    password=BSAdmin.DEFAULT_PASSWORD)
        nu = BSAdmin.objects.get(username=data['username'])
        nu.email = None
        nu.save()
    except DatabaseError:
        return msg_response(1, "用户名已存在")
    if OUTPUT_LOG:
        print(f"{request.user.username} 创建了账号 {data['username']}")
    return msg_response(0)


@require_admin_login
def get_account(request, data):
    user = request.user
    info = {'username': user.username,
            'email': user.email,
            'phone': user.phone}
    return ret_response(0, {'info': info})


@require_admin_login
def modify_account(request, data):
    nd = data['newdata']
    user = request.user
    try:
        if nd.get('username'):
            user.username = nd.get('username')
        if nd.get('password'):
            user.set_password(nd.get('password'))
        if nd.get('email'):
            user.email = nd.get('email')
        if nd.get('phone'):
            user.phone = nd.get('phone')
        user.save()
    except DatabaseError:
        return msg_response(1, "用户名已存在")
    if OUTPUT_LOG:
        print(f"{user.username} 修改了个人信息")
    return msg_response(0)


@require_super_login
def delete_account(request, data):
    BSAdmin.objects.get(username=data['username']).delete()
    if OUTPUT_LOG:
        print(f"{request.user.username} 删除了 {data['username']} 的账号")
    return msg_response(0)


@require_admin_login
def account_list(request, data):
    ps = int(data['pagesize'])
    pn = int(data['pagenum'])
    kw = data['keyword']

    lst = BSAdmin.objects.all()
    if kw != "":
        lst = lst.filter(username__icontains=kw)

    tot = lst.count()
    paginator = Paginator(lst, ps)
    page = paginator.page(pn)
    items = page.object_list.values('username', 'email', 'phone', 'is_superuser')
    items = list(items)
    for x in items:
        x['usertype'] = 'super' if x['is_superuser'] else 'admin'
        del x['is_superuser']

    return ret_response(0, {'items': items, 'total': tot})


@require_admin_login
def is_super(request, data):
    user = request.user
    return ret_response(0, {'issuper': user.is_superuser})


@require_super_login
def reset_password(request, data):
    user = BSAdmin.objects.get(username=data['username'])
    if user is None:
        return msg_response(1, "用户名不存在")
    user.set_password(BSAdmin.DEFAULT_PASSWORD)
    user.save()
    if OUTPUT_LOG:
        print(f"{request.user.username} 重置了 {user.username} 的密码")
    return msg_response(0)


@require_admin_login
def integrity_verification(request, data):
    user = request.user
    integrity = user.email is not None and user.phone is not None
    return ret_response(0, {'integrity': integrity})
