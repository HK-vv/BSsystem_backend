from utils.decorators import require_admin_login


@require_admin_login()
def user_list():
    pass


@require_admin_login()
def user_contest_history():
    pass
