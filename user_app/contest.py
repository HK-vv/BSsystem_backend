import datetime
import traceback
import pytz
from django.core.paginator import Paginator
from django.db import transaction

from bsmodels.models import Contest, BSUser, Registration, ContestProblem, Problem, Record
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
    cur = pytz.UTC.localize(datetime.datetime.now())

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
        with transaction.atomic():
            reg = Registration.objects.get(userid=user, contestid=contest)
            if reg.starttime is None:
                reg.starttime = cur
                reg.currenttime = cur
                reg.save()

        # 计算比赛题目总共数量
        total = ContestProblem.objects.filter(contestid=contest).count()

        return ret_response(0, {'total': total})
    except Registration.DoesNotExist as rdne:
        traceback.print_exc()
        print(rdne.args)
        return msg_response(1, msg=f'您未注册比赛')
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(3)


@require_user_login
def get_next_problem(request, data):
    cid = data['contestid']

    with transaction.atomic():
        reg = Registration.objects.get(userid=request.user_id, contestid_id=cid)
        if not reg:
            return msg_response(1, msg=f"您未注册比赛")
        contest = Contest.objects.get(id=cid)
        reg = Registration.objects.get(userid=request.user_id, contestid_id=cid)
        nc = reg.currentnumber
        tc = reg.currenttime
        ps = contest.get_problemids()
        totn = len(ps)

        t = pytz.UTC.localize(datetime.datetime.now())
        sum = datetime.timedelta(seconds=0)
        for k in range(nc, totn + 1):
            if sum <= t - tc < sum + datetime.timedelta(seconds=ps[k]['dt']):
                break
            sum += datetime.timedelta(seconds=ps[k]['dt'])
        tar = max(k, nc + 1)
        if tar > totn:
            return msg_response(1, msg=f'比赛完成')

        sum = datetime.timedelta(seconds=0)
        for k in range(nc, tar + 1):
            sum += datetime.timedelta(seconds=ps[k]['dt'])
        tardt = min(sum - (t - tc), ps[tar]['dt'])
        assert tardt > datetime.timedelta(seconds=0)

        reg.currentnumber = tar
        reg.save()

    problem = Problem.objects.get(id=ps[tar]['id'])
    fp = {
        'type': problem.type,
        'description': problem.description,
        'options': problem.get_options(),
        'problemnum': tar,
        'time': tardt
    }
    return ret_response(0, fp)


@require_user_login
def submit_answer(request, data):
    cid = data['contestid']
    pn = data['problemnum']
    ans = data['user_answer']

    with transaction.atomic():
        reg = Registration.objects.get(userid=request.user_id, contestid_id=cid)
        if not reg:
            return msg_response(1, msg=f"您未注册比赛")
        nc = reg.currentnumber
        tc = reg.currenttime
        contest = Contest.objects.get(id=cid)
        ps = contest.get_problemids()
        t = pytz.UTC.localize(datetime.datetime.now())

        if t - tc <= datetime.timedelta(seconds=ps[nc]['dt']):
            pass
        else:
            return msg_response(1, msg=f"已超时")

        reg.currenttime = t
        reg.save()
        Record(reg=reg, pno=nc, ans=ans).save()

    return msg_response(0)
