from django.urls import path
from user_app.auth import *
from user_app.profile import *
from user_app.exercise import *

urlpatterns = [
    path('login', login),
    path('logout', logout),
    path('profile', profile),
    path('exercise/collect', collect_problem),
    path('exercise/problem', get_problem),
    path('exercise/problem/check', check),
]
