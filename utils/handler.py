from utils.auxiliary import msg_response

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
    # 根据不同的方法分派给不同的函数进行处理
    method = request.method

    if method in method2handler_table:
        handlerFunc = method2handler_table[method]
        return handlerFunc(request)

    else:
        return msg_response(ret=1, msg="method方法有误")
