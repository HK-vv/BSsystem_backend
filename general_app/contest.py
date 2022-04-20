import datetime

import pytz
from django.core.paginator import Paginator
from django.db.models import Q, F, QuerySet

from bsmodels.models import Contest, ContestProblem, Problem, Registration
from utils.auxilary import ret_response
from utils.decorators import require_nothing


@require_nothing
def contest_list(request, data):
    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    cur = pytz.UTC.localize(datetime.datetime.now())

    lst = Contest.objects.all()

    if data.get('type'):
        type = data['type']

        if type == 'upcoming':
            lst = lst.filter(start__gt=cur)
        elif type == 'history':
            lst = lst.filter(done=True)
        elif type == 'in_progress':
            satisfy = []
            for contest in lst:
                if contest.get_end_time() > cur >= contest.start:
                    satisfy.append(contest.id)
            lst = lst.filter(id__in=satisfy)
        elif type == 'to_be_announced':
            satisfy = []
            for contest in lst:
                if cur >= contest.get_end_time() and not contest.done:
                    satisfy.append(contest.id)
            lst = lst.filter(id__in=satisfy)

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
            'author': contest.authorid.username
        }

        contest_problem = ContestProblem.objects.filter(contestid=contest).order_by('number')
        problems = list(contest_problem.values('problemid', 'duration'))

        problemsid = []

        max_time = 0

        for it in problems:
            problemid = it['problemid']
            if Problem.objects.get(id=problemid):
                problem = Problem.objects.get(id=problemid)
                item['time_limited'][problem.type] = it['duration']
                max_time += it['duration']
            problemsid.append(problemid)

        item['problems'] = problemsid
        item['register_num'] = Registration.objects.filter(contestid=contestid).count()

        if cur < contest.start:
            item['status'] = '未开始'
        elif cur < contest.get_end_time():
            item['status'] = '比赛中'
        elif contest.done:
            item['status'] = '已结束'
        else:
            item['status'] = '待公布成绩'

        items.append(item)

    return ret_response(0, {'items': items, 'total': total})
