from django.urls import path

from admin_app import auth

urlpatterns = [
    path('login', auth.log_in),
    path('logout', auth.log_out),
]
