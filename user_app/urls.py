from django.urls import path
from user_app import auth, profile, exercise, contest

urlpatterns = [
    path('auth/login', auth.login),
    path('auth/logout', auth.logout),
    path('profile', profile.profile),
    path('exercise/collect', exercise.collect_problem),
    path('exercise/problem', exercise.get_problem),
    path('exercise/problem/check', exercise.check),
    path('contest/register', contest.register),
    path('contest/records', contest.records),
]
