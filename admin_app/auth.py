import json

from django.contrib.auth import login


def log_in(request):
    data = json.loads(request.body)

