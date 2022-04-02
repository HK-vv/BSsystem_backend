from django.urls import path
from user_app.auth import *
from user_app.profile import *

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('profile', profile),
]
