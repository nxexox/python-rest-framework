"""
Base classes for views.

"""
from rest_framework.exceptions import ApiException


class BaseApiView(object):
    """
    Base api view.

    """
    def fail(self, detail=None, status=400):
        """
        Raise ApiException for return api exception response.

        :param Optional[dict, str, int, float, list] detail: Body request data. Valid json objects.
        :param int status: Response status code.

        :raise ApiException:

        """
        raise ApiException(detail=detail, status=status)
