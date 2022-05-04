import datetime

import pytz
from django.core.paginator import Paginator
from django.db.models import Q, F, QuerySet

from bsmodels.models import Contest, ContestProblem, Problem, Registration
from utils.auxiliary import ret_response
from utils.decorators import require_nothing


@require_nothing
def contest_list(request, data):
    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    lst = Contest.objects.all()

    if data.get('type'):
        type = data['type'].split(' ')

        satisfy = []
        for contest in lst:
            if contest.get_status() in type:
                satisfy.append(contest.id)
        lst = lst.filter(id__in=satisfy)

    if data.get('author'):
        author = data['author']
        lst = lst.select_related('authorid').filter(authorid__username__icontains=author)

    if data.get('keyword'):
        keyword = data['keyword']
        lst = lst.filter(name__icontains=keyword)

    lst = lst.order_by('-start')

    total = lst.count()
    paginator = Paginator(lst, pagesize)
    page = paginator.page(pagenum)
    items = page.object_list.values()
    temp = list(items)
    items = []

    for x in temp:
        contestid = x['id']
        contest = Contest.objects.get(id=contestid)

        item = {
            'contestid': contest.id,
            'name': contest.name,
            'start': contest.start.strftime('%Y-%m-%d %H:%M:%S'),
            'latest': contest.latest.strftime('%Y-%m-%d %H:%M:%S'),
            'public': contest.password is None,
            'rated': contest.rated,
            'time_limited': {
                "single": 0,
                "multiple": 0,
                "binary": 0,
                "completion": 0
            },
            'author': contest.authorid.username,
            'total_number': contest.count_problem()
        }

        if request.session.get('openid'):
            if Registration.objects.filter(contestid=contestid, userid_id=request.session.get('openid')).exists():
                item['registered'] = True
            else:
                item['registered'] = False

        contest_problem = ContestProblem.objects.filter(contestid=contest) \
            .exclude(problemid__isnull=True).order_by('number')
        problems = list(contest_problem.values('problemid', 'duration'))

        for it in problems:
            problemid = it['problemid']
            if Problem.objects.filter(id=problemid).exists():
                problem = Problem.objects.get(id=problemid)
                item['time_limited'][problem.type] = it['duration']

        item['register_num'] = Registration.objects.filter(contestid=contestid).count()

        if contest.end is None:
            contest.end = contest.get_end_time()

        item['status'] = contest.get_status()

        items.append(item)

    return ret_response(0, {'items': items, 'total': total})
