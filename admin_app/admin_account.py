from utils.auxilary import msg_response
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
def create_account(request):
    pass


@require_admin_login()
def get_account(request):
    pass


@require_admin_login()
def modify_account(request):
    pass


@require_super_login()
def delete_account(request):
    pass


@require_admin_login()
def account_list(request):
    pass


@require_admin_login()
def is_super(request):
    pass


@require_super_login()
def reset_password(request):
    pass


@require_admin_login()
def integrity_verification(request):
    pass
