from django.urls import path
from user_app.auth import *

urlpatterns = [
    path('login', login),
    path('logout', logout),
]
