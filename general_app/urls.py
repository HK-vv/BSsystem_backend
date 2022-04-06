from django.urls import path

from general_app import tag

urlpatterns = [
    path('tag/list', tag.tag_list)
]
