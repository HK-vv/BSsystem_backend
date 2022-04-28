from django.test import TestCase, Client
import pprint
import requests


# Create your tests here.
class Test(TestCase):
    localhost = 'localhost'
    port = '8000'
    cookie = None

    def test_login(self):
        # c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        # response = c.post('/api/user/login', {'username': 'admin', 'password': 'admin'})
        # print(response)
        payload = {
            'code': '061CM3Ha1BE6RC0NiAIa1zU6hf1CM3HK'
        }

        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/auth/login',
                                 json=payload)
        pprint.pprint(response.json())
        # pprint.pprint(response.cookies.values())
        self.cookie = response.cookies

    def test_logout(self):
        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/auth/logout', cookies=self.cookie)
        pprint.pprint(response.json())

    def test_get_info(self):
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/profile', cookies=self.cookie)
        pprint.pprint(response.json())

    def test_modify_info(self, username):
        payload = {
            "newdata": {
                "username": username
            }
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/profile', cookies=self.cookie,
                                 json=payload)
        pprint.pprint(response.json())

    def test_get_problem(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/exercise/problem?id=1', cookies=self.cookie)
        pprint.pprint(response.json())

    def test_check(self, id, answer):
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/exercise/problem/check?problem_id={id}&answer={answer}', cookies=self.cookie)
        pprint.pprint(response.json())

    def test_collect(self, tag, amount):
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/exercise/collect?tag={tag}&amount={amount}',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_register(self):
        self.test_login()
        payload = {
            "contestid": 6,
            'password': 'brainstorm'
        }
        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/contest/register',
                                 cookies=self.cookie, json=payload)
        pprint.pprint(response.json())

    def test_records(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/contest/records?pagesize=4&pagenum=1',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_start(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/contest/start?contestid=4',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_list_contest(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/general/contest/list?pagesize=5'
                                f'&pagenum=1&type=in_progress',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_record(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/contest/result?contestid=2',
                                cookies=self.cookie)
        pprint.pprint(response.json())

    def test_leaderboard(self):
        self.test_login()
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/contest/leaderboard?contestid=2',
                                cookies=self.cookie)
        pprint.pprint(response.json())


if __name__ == '__main__':
    t = Test()
    t.test_login()
    # t.test_modify_info('eddie')
    # t.test_get_info()
    # t.test_collect('语文', 4)
    # t.test_get_problem(3)
    t.test_register()
    t.test_logout()
