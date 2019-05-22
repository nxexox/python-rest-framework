"""
Base classes for views.

"""
import abc

from rest_framework.exceptions import ApiException
from rest_framework.serializers import Serializer


class GetSerializerAbstractMixin(object, metaclass=abc.ABCMeta):
    """
    Class for search serializer in handlers.

    """
    serializer_classes = {}

    @abc.abstractmethod
    @property
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        pass

    def get_serializer(self, key):
        """
        Search serializer.

        :param str key: Key for search. Must be one from `in`, `out`.

        :return: Found serializer or None.
        :rtype: Optional[Type[rest_framework.serializers.Serializer]]

        """
        if key not in ('in', 'out'):
            return None
        serializers = self.serializer_classes.get(self.current_request_method.lower(), dict())

        if isinstance(serializers, dict):
            return serializers.get(key, None)
        elif issubclass(serializers, Serializer):
            return serializers

    def get_response_serializer(self):
        """
        Search Serializer for response.

        :return: Found serializer or None.
        :rtype: Optional[Type[rest_framework.serializers.Serializer]]

        """
        return self.get_serializer('out')

    def get_request_serializer(self):
        """
        Search Serializer for request.

        :return: Found serializer or None.
        :rtype: Optional[Type[rest_framework.serializers.Serializer]]

        """
        return self.get_serializer('in')


class BaseApiView(object):
    """
    Base api view.

    """
    def fail(self, detail=None, status=400):
        """
        Raise ApiException for return api eception response.

        :param Optional[dict, str, int, float, list] detail: Body request data. Valid json objects.
        :param int status: Response status code.

        :raise ApiException:

        """
        raise ApiException(detail=detail, status=status)

