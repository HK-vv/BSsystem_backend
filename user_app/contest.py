import datetime
import traceback
import pytz
from django.core.paginator import Paginator

from bsmodels.models import Contest, BSUser, Registration, ContestProblem, Problem
from utils.auxilary import msg_response, ret_response
from utils.decorators import require_user_login


@require_user_login
def register(request, data):
    contestid = data['contestid']
    openid = request.session['openid']
    user = BSUser.objects.get(openid=openid)
    cur = pytz.UTC.localize(datetime.datetime.now())

    try:
        contest = Contest.objects.get(id=contestid)

        if Registration.objects.filter(contestid=contest, userid=user):
            return msg_response(1, msg='请勿重复注册')

        if contest.latest < cur:
            return msg_response(1, msg=f'比赛{contestid}注册已截止')

        if contest.password is not None:
            if data.get('password'):
                password = data['password']
                if password != contest.password:
                    return msg_response(1, msg='密码错误')
            else:
                return msg_response(1, msg='未填写密码')

        Registration.objects.create(userid=user,
                                    contestid=contest,
                                    regtime=cur)

    except Contest.DoesNotExist as cdne:
        traceback.print_exc()
        print(cdne.args)
        return msg_response(1, msg=f'比赛{contestid}不存在')
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, msg=f'注册失败')

    return msg_response(0)


@require_user_login
def records(request, data):
    openid = request.session['openid']
    user = BSUser.objects.get(openid=openid)

    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    lst = Registration.objects.filter(userid=user)

    cur = pytz.UTC.localize(datetime.datetime.now())

    if data.get('keyword'):
        keyword = data['keyword']
        lst = lst.select_related('contestid').filter(contestid__name__icontains=keyword)

    lst = lst.order_by('-regtime')

    total = lst.count()
    paginator = Paginator(lst, pagesize)
    page = paginator.page(pagenum)
    items = page.object_list.values()
    temp = list(items)
    items = []
    print(temp)
    for x in temp:
        contestid = x['contestid_id']
        contest = Contest.objects.get(id=contestid)

        item = {
            'contestid': contest.id,
            'name': contest.name,
            'start': contest.start.strftime('%Y-%m-%d %H:%M:%S'),
            'latest': contest.latest.strftime('%Y-%m-%d %H:%M:%S'),
            'regtime': x['regtime'].strftime('%Y-%m-%d %H:%M:%S'),
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

        for it in problems:
            problemid = it['problemid']
            if Problem.objects.get(id=problemid):
                problem = Problem.objects.get(id=problemid)
                item['time_limited'][problem.type] = it['duration']

        item['register_num'] = Registration.objects.filter(contestid=contestid).count()

        if cur < contest.start:
            item['status'] = '未开始'
        elif cur < contest.end:
            item['status'] = '比赛中'
        elif contest.announced:
            item['status'] = '已结束'
        else:
            item['status'] = '待公布成绩'

        items.append(item)

    return ret_response(0, {'items': items, 'total': total})
