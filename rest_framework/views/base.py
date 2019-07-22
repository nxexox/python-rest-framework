"""
Base classes for views.

"""
from rest_framework.exceptions import ApiException


class BaseApiView(object):
    """
    Base api view.

    """
    # For settings run dispatch method
    use_dispatch = True

    # Class for create Response object. Default Interface: Response(data: dict, status: int)
    # Data - dict json data for return. status - response server status code.
    response_class = None

    # Response Content Type, default: application/json
    response_content_type = 'application/json'

    def fail(self, detail=None, status=400):
        """
        Raise ApiException for return api exception response.

        :param Optional[dict, str, int, float, list] detail: Body request data. Valid json objects.
        :param int status: Response status code.

        :raise ApiException:

        """
        raise ApiException(detail=detail, status=status)

    def _dispatch(self, method, *args, **kwargs):
        """
        Code after, before call request handler.

        :param Callable method: Method handler for call.

        """
        try:
            return method(*args, **kwargs)
        except ApiException as e:
            # TODO: Not security. e.detail maybe anything
            return self.response_class.__func__(
                {'errors': e.detail},
                status=e.status or 400,
                content_type=self.response_content_type
            )
