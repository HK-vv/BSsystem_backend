from bsmodels.models import Tag
from utils.auxilary import ret_response
from utils.decorators import require_nothing


@require_nothing
def tag_list(request, data):
    tags = Tag.objects.all().values_list('name', flat=True)
    tot = tags.count()
    return ret_response(0, {'tags': tags, 'total': tot})
