from django.urls import path

from general_app import tag, contest, rating

urlpatterns = [
    path('tag/list', tag.tag_list),
    path('contest/list', contest.contest_list),
    path('rating/leaderboard', rating.leaderboard),
    path('rating/update', rating.update),
]
