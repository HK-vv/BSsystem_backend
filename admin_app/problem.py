from django.core.paginator import Paginator
from django.db import transaction, DatabaseError
from django.forms import model_to_dict

from brainstorm.settings import OUTPUT_LOG
from utils.decorators import *
from brainstorm import settings
import os
import pandas as pd
from utils.auxiliary import *
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

    # 单选 多选
    if type in ['single', 'multiple']:
        if A and B and C and D:
            too_long = []
            if len(A) > 25:
                too_long.append("选项1")
            if len(B) > 25:
                too_long.append("选项2")
            if len(C) > 25:
                too_long.append("选项3")
            if len(D) > 25:
                too_long.append("选项4")

            if len(too_long) > 0:
                # 将too_long列表的字符连接，并用顿号分隔
                errs = "、".join(too_long)
                raise Exception(f"{errs}过长")
            if type == 'single':
                if len(answer) != 1:
                    raise Exception("单选题只能有一个答案")
            elif type == 'multiple':
                if len(answer) > 4:
                    raise Exception("多选题最多只能有四个答案")
                for char in answer:
                    temp = {
                        'A': False,
                        'B': False,
                        'C': False,
                        'D': False
                    }
                    if temp[char]:
                        raise Exception("多选题不能有重复的答案")
                    temp[char] = True
            for char in answer:
                if char not in ['A', 'B', 'C', 'D']:
                    raise Exception("答案错误")

            problem.A = A
            problem.B = B
            problem.C = C
            problem.D = D
        else:
            raise Exception("选项为空")
    # 判断
    elif type == 'binary':
        if answer not in ['A', 'B']:
            raise Exception("答案错误")

        problem.A = '正确'
        problem.B = '错误'
        problem.C = problem.D = None
    # 填空
    elif type == 'completion':
        problem.answer = problem.answer.replace('，', ',')
        problem.A = problem.B = problem.C = problem.D = None
    # 异常
    else:
        raise Exception("题目类型错误")

    problem.type = type
    return problem


def excel2problems(table, user):
    errors = []
    try:
        with transaction.atomic():
            problems = []
            for i in range(len(table)):
                data = table.iloc[i]
                try:
                    problem = data2problem(data, user)
                    problem.save()
                    problems.append(problem)
                except Exception as e:
                    errors.append(f"第{i + 2}行 {e.args[0]}")
                    continue

            if len(errors) > 0:
                str = ", \n".join(errors)
                raise Exception(str)

            return problems

    except Exception as e:
        raise Exception(e.args[0])


@require_admin_login
def batch_add(request, data):
    tags = data['tags']
    tags = tags.split(',')
    user = request.user

    # print(tags, type(tags))
    # 获取上传文件的数据
    file = request.FILES.get('file')
    file_name = file.name

    try:
        table = pd.read_excel(file, dtype={'题目': 'str', '选项1': 'str', '选项2': 'str', '选项3': 'str', '选项4': 'str',
                                           '正确答案': 'str'})
        table.rename(columns={'题目': 'description', '题型': 'type', '选项1': 'A', '选项2': 'B', '选项3': 'C', '选项4': 'D',
                              '正确答案': 'answer', '是否公开': 'public'}, inplace=True)
        table.replace({"public": {'公开': True, '不公开': False}}, inplace=True)
        table.replace({"type": {'单选题': 'single', '多选题': 'multiple',
                                '判断题': 'binary', '填空题': 'completion'}}, inplace=True)
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, msg='文件格式有误')

    table = table.where(table.notnull(), None)
    print(table)

    try:
        problems = excel2problems(table, user)
    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, msg=e.args[0])

    tagsid = list(Tag.objects.filter(name__in=tags).values_list('id', flat=True))

    for id in tagsid:
        for problem in problems:
            ProblemTag.objects.create(problemid=problem,
                                      tagid_id=id)

    if SAVED:
        # 拼接文件路径
        path = os.path.join(settings.BASE_DIR, FOLDER_NAME)
        if not os.path.exists(path):
            os.mkdir(path)
        with open(os.path.join(path, file_name), 'wb')as f:
            for i in file.chunks():
                f.write(i)

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

    lst = lst.order_by('id')
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
        traceback.print_exc()
        print(e.args)
        return msg_response(1, e.args[0])

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
        return msg_response(1, e.args[0])

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


@require_admin_login
def problem_detail(request, data):
    problemid = data['problemid']
    try:
        problem = model_to_dict(Problem.objects.get(id=problemid))
        info = {'problemid': problemid,
                'type': problem['type'],
                'description': problem['description'],
                'answer': problem['answer'],
                'public': problem['public']}

        tagsid = list(ProblemTag.objects.filter(problemid_id=problemid).values_list('tagid', flat=True))
        tags = list(Tag.objects.filter(id__in=tagsid).values_list('name', flat=True))
        info['tags'] = tags

        options = []
        for i in range(4):
            if problem[chr(ord('A') + i)] is not None:
                options.append(problem[chr(ord('A') + i)])
        info['options'] = options

        authorid = problem['authorid']
        author = BSAdmin.objects.get(id=authorid).username
        info['author'] = author

    except Exception as e:
        traceback.print_exc()
        print(e.args)
        return msg_response(1, f'题目{problemid}不存在')

    return ret_response(0, {'info': info})
