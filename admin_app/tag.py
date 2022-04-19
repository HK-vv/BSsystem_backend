from django.db import DatabaseError

from brainstorm.settings import OUTPUT_LOG
from bsmodels.models import Tag
from utils.auxilary import msg_response
from utils.decorators import require_super_login
from utils.handler import dispatcher_base


def tag_dispatcher(request):
    method2handler = {
        'POST': modify_tag,
        'PUT': add_tag,
        'DELETE': delete_tag
    }
    return dispatcher_base(request, method2handler)


@require_super_login
def add_tag(request, data):
    try:
        Tag.objects.create(name=data['tag']).save()
    except DatabaseError:
        return msg_response(1, "标签已存在")

    if OUTPUT_LOG:
        print(f"{request.user.username} 添加了标签 {data['tag']}")

    return msg_response(0)


@require_super_login
def modify_tag(request, data):
    try:
        tag = Tag.objects.get(name=data['oldname'])
        tag.name = data['newname']
        tag.save()
    except DatabaseError:
        return msg_response(1, "标签已存在")
    return msg_response(0)


@require_super_login
def delete_tag(request, data):
    Tag.objects.get(name=data['tag']).delete()

    if OUTPUT_LOG:
        print(f"{request.user.username} 删除了标签 {data['tag']}")

    return msg_response(0)
