from bsmodels.models import Tag
from utils.auxiliary import ret_response
from utils.decorators import require_nothing


@require_nothing
def tag_list(request, data):
    tags = Tag.objects.all().values_list('name', flat=True)
    tot = tags.count()
    tags = list(tags)
    return ret_response(0, {'tags': tags, 'total': tot})
