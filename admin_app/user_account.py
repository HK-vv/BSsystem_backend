from django.core.paginator import Paginator
from django.db.models import Count

from bsmodels.models import BSUser, Contest, Registration
from utils.auxilary import ret_response, dict_list_decorator
from utils.decorators import require_admin_login


@require_admin_login
def user_list(request, data):
    ps = int(data['pagesize'])
    pn = int(data['pagenum'])
    kw = data.get('keyword')
    st = data.get('sort_by_rating')

    lst = BSUser.objects.all()
    if kw != "":
        lst = lst.filter(username__icontains=kw)
    if st == 'descending':
        lst = lst.order_by('-rating')
    elif st == 'ascending':
        lst = lst.order_by('rating')
    else:
        lst = lst.order_by('openid')

    tot = lst.count()
    page = Paginator(lst, ps).page(pn)
    items = page.object_list.values('username', 'rating', matches=Count('registration'))
    items = list(items)

    return ret_response(0, {'items': items, 'total': tot})


@require_admin_login
def user_contest_history(request, data):
    ps = int(data['pagesize'])
    pn = int(data['pagenum'])
    username = data['username']
    kw = data.get('keyword')

    lst = Registration.objects.filter(userid__username=username)
    if kw is not None and kw != "":
        lst = lst.filter(contestid__name__icontains=kw)
    tot = lst.count()
    page = Paginator(lst, ps).page(pn)
    items = page.object_list.values('contestid',
                                    'contestid__name',
                                    'contestid__rated',
                                    'score',
                                    'beforerating',
                                    'afterrating',
                                    'timecost',
                                    'rank')
    items = list(items)
    items = dict_list_decorator(items, mp={'contestid__name': "name",
                                          'contestid__rated': "rated",
                                          'beforerating': "before_rating",
                                          'afterrating': "after_rating"})
    return ret_response(0, {'items': items, 'total': tot})
