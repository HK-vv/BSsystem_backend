from django.urls import path
from user_app import auth
from user_app import profile
from user_app import exercise

urlpatterns = [
    path('auth/login', auth.login),
    path('auth/logout', auth.logout),
    path('profile', profile.profile),
    path('exercise/collect', exercise.collect_problem),
    path('exercise/problem', exercise.get_problem),
    path('exercise/problem/check', exercise.check),
]
