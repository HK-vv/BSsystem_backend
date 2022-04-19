from django.urls import path

from general_app import tag, contest

urlpatterns = [
    path('tag/list', tag.tag_list),
    path('contest/list', contest.contest_list)
]
