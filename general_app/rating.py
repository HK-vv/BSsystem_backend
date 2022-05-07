import traceback
from django.core.paginator import Paginator
from bsmodels.models import BSUser, update_rank
from utils.auxiliary import ret_response
from utils.decorators import require_nothing


@require_nothing
def leaderboard(request, data):
    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    lst = BSUser.objects.all()

    if data.get('keyword'):
        keyword = data['keyword']
        lst = lst.filter(username__icontains=keyword)

    lst = lst.order_by('rank')

    total = lst.count()
    paginator = Paginator(lst, pagesize)
    page = paginator.page(pagenum)
    items = page.object_list.values('username', 'rating', 'rank')
    items = list(items)

    return ret_response(0, {'items': items, 'total': total})


@require_nothing
def update(request, data):
    try:
        update_rank()
        return ret_response(0)
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return ret_response(1)
