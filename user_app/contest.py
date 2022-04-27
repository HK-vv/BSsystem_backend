import datetime
import traceback
import pytz
from django.core.paginator import Paginator
from django.db import transaction

from bsmodels.models import Contest, BSUser, Registration, ContestProblem, Problem, Record
from utils.auxilary import msg_response, ret_response, get_current_time
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
                                    regtime=cur,
                                    currentnumber=0)

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
def contest_history(request, data):
    openid = request.session['openid']
    user = BSUser.objects.get(openid=openid)

    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    lst = Registration.objects.filter(userid=user)

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

        item['status'] = contest.get_status()

        items.append(item)

    return ret_response(0, {'items': items, 'total': total})


@require_user_login
def start(request, data):
    contestid = data['contestid']
    user = BSUser.objects.get(openid=request.session['openid'])
    cur = get_current_time()

    try:
        contest = Contest.objects.get(id=contestid)
    except Contest.DoesNotExist as cdne:
        traceback.print_exc()
        print(cdne.args)
        return msg_response(1, msg=f'比赛{contestid}不存在')

    if contest.start > cur:
        return msg_response(1, msg=f'比赛{contestid}未开始')

    elif contest.end < cur or contest.announced:
        return msg_response(1, msg=f'比赛{contestid}已结束')

    try:
        Registration.objects.get(userid=user, contestid=contest).start()
        total = ContestProblem.objects.filter(contestid=contest).count()

        return ret_response(0, {'total': total})
    except Registration.DoesNotExist as rdne:
        traceback.print_exc()
        print(rdne.args)
        return msg_response(1, msg=f'您未注册比赛')


@require_user_login
def get_problem(request, data):
    cid = data['contestid']
    reg = Registration.objects.get(contestid_id=cid, userid=request.user)
    if not reg:
        return msg_response(1, msg=f"您未注册比赛")

    problem, nc, dt = reg.get_current_problem()
    fp = {
        'type': problem.type,
        'description': problem.description,
        'options': problem.get_options(),
        'problemnum': nc,
        'time': dt,
        'total_number': reg.contestid.count_problem()
    }
    return ret_response(0, fp)


@require_user_login
def submit_answer(request, data):
    cid = data['contestid']
    pn = data['problemnum']
    ans = data['user_answer']
    try:
        reg = Registration.objects.get(userid=request.user, contestid_id=cid)
    except Registration.DoesNotExist as rdne:
        traceback.print_exc()
        print(rdne.args)
        return msg_response(1, msg=f"您未注册比赛")

    try:
        with transaction.atomic():
            r = reg.submit_current(ans, pn)
            reg.next_problem()
    except Exception as e:
        if isinstance(e.args[0], str):
            return msg_response(1, e.args[0])
        raise e

    if r == "timeout":
        return msg_response(0, "Timeout")
    else:
        return msg_response(0, "Success")


@require_user_login
def result(request, data):
    user = request.user
    contestid = data['contestid']
    try:
        contest = Contest.objects.get(id=contestid)
        if contest.get_status() in ['upcoming', 'running', 'shut']:
            return msg_response(1, msg=f'比赛{contestid}未结束')

        reg = Registration.objects.get(userid=user, contestid=contest)
        problems = contest.get_problems()

        items = []

        for no in problems.keys():
            problemid = problems[no]['id']
            item = {
                'problemno': no,
                'problemid': problemid,
                # 'answer': 'A'
            }

            if Record.objects.filter(userid=user, contestid=contest, problemid_id=problemid).exists():
                record = Record.objects.get(userid=user, contestid=contest, problemid_id=problemid)
                item['correct'] = True if record.result == 'T' else False
                item['submitted'] = record.submitted
            else:
                item['correct'] = False
                item['submitted'] = None

            if Problem.objects.filter(id=problemid).exists():
                item['answer'] = Problem.objects.get(id=problemid).answer
            else:
                item['answer'] = None

            items.append(item)

    except Contest.DoesNotExist as cdne:
        traceback.print_exc()
        print(cdne.args)
        return msg_response(1, msg=f'比赛{contestid}不存在')
    except Registration.DoesNotExist as rdne:
        traceback.print_exc()
        print(rdne.args)
        return msg_response(1, msg=f'您未注册比赛')
    except Record.DoesNotExist as rdne:
        traceback.print_exc()
        print(rdne.args)
        return msg_response(1, msg=f'您未参加比赛')
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(3)

    return ret_response(0, {'items': items,
                            'total': len(problems),
                            'score': reg.score,
                            'timecost': reg.timecost,
                            'rank': reg.rank,
                            'before_rating': reg.beforerating,
                            'changed_rating': reg.afterrating - reg.beforerating
                            })
