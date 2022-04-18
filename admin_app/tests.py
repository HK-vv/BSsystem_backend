import json

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
                "Codeforces",
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
          "problems": list(range(80,85))
        }
        response = requests.put(f'http://{self.localhost}:{self.port}/api/admin/problem/batch/delete',
                                cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    # def test_batch_add(self):
    #     self.login()
    #     with open('./files/test.xlsx', 'rb') as fp:
    #         response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/problem/batch/add',
    #                                  cookies=self.cookie, files=fp)
    #     pprint.pprint(response.json())
