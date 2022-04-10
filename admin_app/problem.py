from django.db import transaction
from utils.decorators import *
from brainstorm import settings
import os
import pandas as pd
from utils.auxilary import *
import openpyxl
from bsmodels.models import Problem
from bsmodels.models import Tag
from bsmodels.models import ProblemTag

FOLDER_NAME = 'files'
SAVED = True
pd.set_option('display.max_columns', None)


def data2problem(table, line, user):
    data = table.iloc[line]

    description = data['题目']
    type = data['题型']
    A = data['选项1']
    B = data['选项2']
    C = data['选项3']
    D = data['选项4']
    answer = data['正确答案']
    public = True if data['是否公开'] == '公开' else False

    problem = Problem.objects.create(description=description,
                                     answer=answer,
                                     public=public,
                                     authorid=user)

    # 单选 多选
    if type in ['单选题', '多选题']:
        if type == '单选题':
            type = 'single'
        else:
            type = 'multiple'
        if A and B and C and D:
            problem.A = A
            problem.B = B
            problem.C = C
            problem.D = D
        else:
            raise Exception(f"第{line + 2}行选项为空")
    # 判断
    elif type == '判断题':
        type = 'binary'
        problem.A = '正确'
        problem.B = '错误'
    # 填空
    elif type == '填空题':
        type = 'completion'
    else:
        raise Exception(f"第{line + 2}行题目类型错误")

    problem.type = type
    problem.save()
    return problem


def excel2problems(table, user):
    try:
        with transaction.atomic():
            problems = []
            for i in range(len(table)):
                problem = data2problem(table, i, user)
                problems.append(problem)
            return problems

    except Exception as e:
        raise Exception(f"第{i + 2}行格式错误")


@require_admin_login()
def batch_add(request, data):
    tags = data['tags']
    user = request.user

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
    except Exception:
        return msg_response(1, msg='文件格式有误')

    table = table.where(table.notnull(), None)
    # print(table)
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

    return msg_response(0)
