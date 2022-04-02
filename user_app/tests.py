from django.test import TestCase, Client
import pprint
import requests


# Create your tests here.
class Test(TestCase):
    localhost = 'localhost'
    port = '8080'
    cookie = None

    def test_login(self):
        # c = Client(HTTP_USER_AGENT='Mozilla/5.0')
        # response = c.post('/api/user/login', {'username': 'admin', 'password': 'admin'})
        # print(response)
        payload = {
            'code': '061CM3Ha1BE6RC0NiAIa1zU6hf1CM3HK'
        }

        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/login',
                                 json=payload)
        pprint.pprint(response.json())
        # pprint.pprint(response.cookies.values())
        self.cookie = response.cookies

    def test_logout(self):
        response = requests.post(f'http://{self.localhost}:{self.port}/api/user/logout', cookies=self.cookie)
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

    def test_get_problem(self, id):
        response = requests.get(f'http://{self.localhost}:{self.port}/api/user/exercise/problem?id={id}', cookies=self.cookie)
        pprint.pprint(response.json())


if __name__ == '__main__':
    t = Test()
    t.test_login()
    t.test_get_problem(3)
    t.test_logout()
