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

        # with open('data/111.jpg', 'rb') as fp:
        #     response = client.post(url, data={'file': fp})
        #     json_resp = json.loads(response.content)
        #     self.assertTrue('url' in json_resp)
        #     self.assertEquals(len(json_resp), 1)

        response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/auth/login',
                                 json=payload)
        pprint.pprint(response.json())
        # pprint.pprint(response.cookies.values())
        self.cookie = response.cookies

    # def test_logout(self):
    #     self.login()
    #
    #     response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/auth/logout', cookies=self.cookie)
    #     pprint.pprint(response.json())

    # def test_batch_add(self):
    #     self.login()
    #     with open('./files/test.xlsx', 'rb') as fp:
    #         response = requests.post(f'http://{self.localhost}:{self.port}/api/admin/problem/batch/add',
    #                                  cookies=self.cookie, files=fp)
    #     pprint.pprint(response.json())
