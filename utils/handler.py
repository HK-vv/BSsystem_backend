import json
from utils.auxilary import msg_response

'''
method2handler_table 写法:
method2handler = {
    'GET'   : get_info,
    'POST'  : modify_info,
    'PUT'   : add_info,
    'DELETE': del_info
}
四种方法均可省略不写
'''


def dispatcher_base(request, method2handler_table):
    # 将请求参数统一放入request 的 params 属性中，方便后续处理

    # GET请求 参数 在 request 对象的 GET属性中
    if request.method == 'GET':
        request.params = request.GET

    # POST/PUT/DELETE 请求 参数 从 request 对象的 body 属性中获取
    elif request.method in ['POST', 'PUT', 'DELETE']:
        # 根据接口，POST/PUT/DELETE 请求的消息体都是 json格式
        request.params = json.loads(request.body)

    # 根据不同的方法分派给不同的函数进行处理
    method = request.method
    if method in method2handler_table:
        handlerFunc = method2handler_table[method]
        return handlerFunc(request)

    else:
        return msg_response(ret=1, msg="method方法有误")
