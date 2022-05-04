from brainstorm.settings import OUTPUT_LOG
from utils.auxiliary import output_request_info


class OutputRequestInformationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        if OUTPUT_LOG:
            output_request_info(request)

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response


