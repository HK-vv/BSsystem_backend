import traceback

from django.core.paginator import Paginator
from django.db.models import Count

from bsmodels.models import BSUser, Contest, Registration, Record, Problem
from utils.auxiliary import ret_response, dict_list_decorator, msg_response
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


@require_admin_login
def user_contest_result(request, data):
    cid = int(data['contestid'])
    username = data['username']
    try:
        contest = Contest.objects.get(id=cid)
        user = BSUser.objects.get(username=username)
        reg = Registration.objects.get(userid=user, contestid=contest)
    except Exception as e:
        print(e.args)
        return msg_response(1, "something doesn't exist")

    tot = contest.count_problem()
    items = []
    for i in range(1, tot + 1):
        if Record.objects.filter(registerid=reg, problemno=i).exists():
            rec = Record.objects.get(registerid=reg, problemno=i)
        else:
            rec = Record.create(reg=reg, pno=i, ans="")
        problem = rec.get_problem()
        items.append({'problemno': i,
                      'problemid': problem.id,
                      'correct': rec.result == 'T',
                      'submitted': rec.submitted,
                      'answer': problem.answer})

    return ret_response(0, {'items': items, 'total': tot})
