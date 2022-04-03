from django.urls import path

from admin_app import auth

urlpatterns = [
    path('auth/login', auth.log_in),
    path('auth/logout', auth.log_out),
]
