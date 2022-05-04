from datetime import *
import json

import pytz
from django.test import TestCase, Client
import pprint
import requests


# Create your tests here.
class Test(TestCase):
    localhost = 'localhost'
    port = '8000'
    cookie = None

    def login(self):
        # url = '/api/admin/auth/login'
        # client = Client()

        payload = {
            'username': 'super',
            'password': '123456'
        }

        # resp = client.post(url, data=payload,
        #                         content_type='application/json')
        # result = resp.json()
        # pprint.pprint(result)

        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/auth/login',
                                 json=payload)
        pprint.pprint(response.json())
        # pprint.pprint(response.cookies.values())
        self.cookie = response.cookies

    def logout(self):
        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/auth/logout', cookies=self.cookie)
        pprint.pprint(response.json())

    def test_batch_public(self):
        self.login()
        payload = {
            "problems": [
                100,
                15,
                14,
                25,
                39
            ]
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/problem/batch/public',
                                 cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_add_problem(self):
        self.login()
        payload = {
            "type": "multiple",
            "tags": [
                "算法",
                "语文"
            ],
            "description": "请选出所有OJ",
            "options": [
                "Codeforce",
                "DBforces",
            ],
            "answer": "ABC",
            "public": True
        }
        response = requests.put(f'http://{self.localhost}:{self.port}/api/admin/problem',
                                cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_get_problem(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/admin/problem?pagesize=10&pagenum=1&'
                                f'author=abc',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_del_problem(self):
        self.login()
        payload = {
            "problems": list(range(100, 105))
        }
        response = requests.put(f'http://{self.localhost}:{self.port}/api/admin/problem/batch/delete',
                                cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_modify_account(self):
        self.login()
        payload = {
            "newdata": {
                "username": "eddie",
                "password": "111111",
                "email": "19182605@buaa.edu.cn",
                "phone": "18800000001"
            }
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/admin_account',
                                 cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_reset(self):
        self.login()
        payload = {
            "username": "eddie"
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/admin_account/reset_password',
                                 cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_add_contest(self):
        self.login()
        payload = {
            "name": "testeddie",
            "start": "2022-04-28 20:10:00",
            "latest": "2022-04-28 20:30:00",
            "password": "",
            "rated": True,
            "time_limited": {
                "single": 30,
                "multiple": 40,
                "binary": 30,
                "completion": 60
            },
            "problems": [
                1,15,32,55,42,60
            ],
            "ordered": False
        }

        response = requests.put(f'http://{self.localhost}:{self.port}/api/admin/contest',
                                cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_get_contest(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/admin/contest?contestid=2',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_modify_contest(self):
        self.login()
        payload = {
            "contestid": 4,
            "newdata": {
                "name": "April Fools Day Contest 2023",
                "start": "2022-04-01 22:35:00",
                "latest": "2024-04-01 22:45:00",
                "password": "brainstorm",
                "rated": True,
                "time_limited": {
                    "single": 30,
                    "multiple": 40,
                    "binary": 30,
                    "completion": 60
                },
                "problems": [
                    50, 51, 52
                ],
                "ordered": False
            }
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/contest',
                                 cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

        self.test_get_contest()

    def test_list_contest(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/general/contest/list?pagesize=5'
                                f'&pagenum=1&type=upcoming+finished&author=eddie',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_problem(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/admin/problem/detail?problemid=225',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_leaderboard(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/admin/contest/leaderboard?'
                                f'contestid=2&pagesize=5&pagenum=1',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_statistics(self):
        self.login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/admin/contest/statistics?contestid=2',
                                cookies=self.cookie)
        pprint.pprint(response.json())
