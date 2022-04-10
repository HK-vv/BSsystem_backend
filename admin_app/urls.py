from django.urls import path
from admin_app import auth, admin_account, user_account, problem

urlpatterns = [
    path('auth/login', auth.log_in),
    path('auth/logout', auth.log_out),
    path('admin_account', admin_account.root_dispatcher),
    path('admin_account/list', admin_account.account_list),
    path('admin_account/issuper', admin_account.is_super),
    path('admin_account/reset_password', admin_account.reset_password),
    path('admin_account/integrity_verification', admin_account.integrity_verification),
    path('user_account/list', user_account.user_list),
    path('user_account/contest/history', user_account.user_contest_history),
    path('problem/batch/add', problem.batch_add)
]
