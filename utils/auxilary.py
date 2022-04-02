from django.http import JsonResponse


def msg_response(ret, msg=None):
    if msg is None:
        return JsonResponse({'ret': ret})
    return JsonResponse({'ret': ret, 'msg': msg})
