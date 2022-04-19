from django.core.paginator import Paginator
from django.db import transaction, DatabaseError

from brainstorm.settings import OUTPUT_LOG
from utils.decorators import *
from brainstorm import settings
import os
import pandas as pd
from utils.auxilary import *
import openpyxl
from bsmodels.models import Problem
from bsmodels.models import Tag
from bsmodels.models import ProblemTag
from bsmodels.models import BSAdmin
from utils.handler import dispatcher_base

FOLDER_NAME = 'files'
SAVED = True
pd.set_option('display.max_columns', None)


def data2problem(data, user):
    description = data['description']
    type = data['type']
    A = data['A']
    B = data['B']
    C = data['C']
    D = data['D']
    answer = data['answer']
    public = data['public']

    # an alternative way to do this
    problem = Problem(description=description,
                      answer=answer,
                      public=public,
                      authorid=user)

    # problem = Problem.objects.create(description=description,
    #                                  answer=answer,
    #                                  public=public,
    #                                  authorid=user)

    # 单选 多选
    if type in ['single', 'multiple']:
        if A and B and C and D:
            problem.A = A
            problem.B = B
            problem.C = C
            problem.D = D
        else:
            raise Exception("该行选项为空")
    # 判断
    elif type == 'binary':
        problem.A = '正确'
        problem.B = '错误'
        problem.C = problem.D = None
    # 填空
    elif type == 'completion':
        problem.A = problem.B = problem.C = problem.D = None
    # 异常
    else:
        raise Exception("题目类型错误")

    problem.type = type
    return problem


def excel2problems(table, user):
    try:
        with transaction.atomic():
            problems = []
            for i in range(len(table)):
                data = table.iloc[i]
                problem = data2problem(data, user)
                problem.save()
                problems.append(problem)
            return problems

    except Exception:
        raise Exception(f"第{i + 2}行格式错误")


@require_admin_login
def batch_add(request, data):
    tags = data['tags']
    tags = tags.split(',')
    user = request.user

    # print(tags, type(tags))
    # 获取上传文件的数据
    file = request.FILES.get('file')
    file_name = file.name

    if SAVED:
        # 拼接文件路径
        path = os.path.join(settings.BASE_DIR, FOLDER_NAME)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, file_name), 'wb')as f:
            for i in file.chunks():
                f.write(i)

    try:
        table = pd.read_excel(file)
        table.rename(columns={'题目': 'description', '题型': 'type', '选项1': 'A', '选项2': 'B', '选项3': 'C', '选项4': 'D',
                              '正确答案': 'answer', '是否公开': 'public'}, inplace=True)
        table.replace({"public": {'公开': True, '不公开': False}}, inplace=True)
        table.replace({"type": {'单选题': 'single', '多选题': 'multiple',
                                '判断题': 'binary', '填空题': 'completion'}}, inplace=True)
    except Exception:
        return msg_response(1, msg='文件格式有误')

    table = table.where(table.notnull(), None)
    print(table)

    try:
        problems = excel2problems(table, user)
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, msg=e.args)

    tagsid = list(Tag.objects.filter(name__in=tags).values_list('id', flat=True))

    for id in tagsid:
        for problem in problems:
            ProblemTag.objects.create(problemid=problem,
                                      tagid_id=id)

    if OUTPUT_LOG:
        print(f"{user.username} 批量添加了题目")

    return msg_response(0)


@require_admin_login
def batch_public(request, data):
    problems = data['problems']
    user = request.user
    try:
        with transaction.atomic():
            for problemid in problems:
                problem = Problem.objects.get(id=problemid)
                if problem.authorid != user and not user.is_superuser:
                    return msg_response(1, msg='权限不足')
                else:
                    problem.public = True
                    problem.save()
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, f'题目{problemid}不存在')

    if OUTPUT_LOG:
        print(f"{user.username} 批量公开了题目 {str(problems)}")

    return ret_response(0)


def problem_dispatcher(request):
    method2handler = {
        'GET': get_problem,
        'POST': modify_problem,
        'PUT': add_problem
    }
    return dispatcher_base(request, method2handler)


@require_admin_login
def get_problem(request, data):
    pagesize = int(data['pagesize'])
    pagenum = int(data['pagenum'])

    lst = Problem.objects.all()

    if 'type' in data and data['type'] != "":
        type = data['type'].split(' ')
        lst = lst.filter(type__in=type)

    if 'tags' in data and data['tags'] != "":
        tags = data['tags'].split(' ')
        tags = list(Tag.objects.filter(name__in=tags))
        problemsid = list(ProblemTag.objects.filter(tagid__in=tags).values_list('problemid', flat=True))
        lst = lst.filter(id__in=problemsid)

    if 'author' in data and data['author'] != "":
        author = data['author']
        author = BSAdmin.objects.filter(username__icontains=author)
        lst = lst.filter(authorid__in=author)

    if 'public' in data and data['public'] != "":
        public = True if data['public'] == '1' else False
        lst = lst.filter(public=public)

    if 'keyword' in data and data['keyword'] != "":
        keyword = data['keyword']
        lst = lst.filter(description__icontains=keyword)

    total = lst.count()
    paginator = Paginator(lst, pagesize)
    page = paginator.page(pagenum)
    items = page.object_list.values()
    temp = list(items)
    items = []

    for x in temp:
        problemid = x['id']
        item = {'problemid': problemid,
                'type': x['type'],
                'description': x['description'],
                'answer': x['answer'],
                'public': x['public']}

        tagsid = list(ProblemTag.objects.filter(problemid_id=problemid).values_list('tagid', flat=True))
        tags = list(Tag.objects.filter(id__in=tagsid).values_list('name', flat=True))
        item['tags'] = tags

        options = []
        for i in range(4):
            if x[chr(ord('A') + i)] is not None:
                options.append(x[chr(ord('A') + i)])
        item['options'] = options

        authorid = x['authorid_id']
        author = BSAdmin.objects.get(id=authorid).username
        item['author'] = author

        items.append(item)

    return ret_response(0, {'items': items, 'total': total})


@require_admin_login
def modify_problem(request, data):
    user = request.user
    id = data['problemid']
    nd = data['newdata']
    tg = nd['tags']

    prob = Problem.objects.get(id=id)
    author = prob.authorid
    if prob.authorid != user and not user.is_superuser:
        return msg_response(1, "权限不足")

    for i in range(4):
        nd[chr(ord('A') + i)] = None if i >= len(nd['options']) \
            else nd['options'][i]
    del nd['options']

    try:
        np = data2problem(nd, author)
        np.id = prob.id
    except Exception as e:
        return msg_response(1, e.args)

    try:
        np.save()
        # update tags now
        ProblemTag.objects.filter(problemid_id=id).delete()
        for t in tg:
            tag = Tag.objects.get(name=t)
            ProblemTag.objects.create(problemid=prob, tagid=tag).save()
    except DatabaseError:
        return msg_response(1, "修改失败")

    if OUTPUT_LOG:
        print(f"{user.username} 修改了题目 {id}")

    return msg_response(0)


@require_admin_login
def add_problem(request, data):
    user = request.user
    try:
        info = {'type': data['type'],
                'description': data['description'],
                'answer': data['answer'],
                'public': data['public']}

        for i in range(4):
            info[chr(ord('A') + i)] = None if i >= len(data['options']) \
                else data['options'][i]

        problem = data2problem(info, user)
        problem.save()

        tags = data['tags']
        tagsid = list(Tag.objects.filter(name__in=tags).values_list('id', flat=True))

        for id in tagsid:
            ProblemTag.objects.create(problemid=problem,
                                      tagid_id=id)

    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, '题目格式有误')

    if OUTPUT_LOG:
        print(f"{user.username} 添加了题目 {problem.id}")

    return msg_response(0)


@require_admin_login
def del_problem(request, data):
    problems = data['problems']
    user = request.user
    try:
        with transaction.atomic():
            for id in problems:
                problem = Problem.objects.get(id=id)
                if problem.authorid != user and not user.is_superuser:
                    return msg_response(1, f'题目{id}不是您创建的题目')
                problem.delete()
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, f'题目{id}不存在')

    if OUTPUT_LOG:
        print(f"{user.username} 删除了题目 {str(problems)}")

    return msg_response(0)
