"""
Mixins for views.

"""
import abc
import logging

import six

from rest_framework.serializers import Serializer
from rest_framework.views.paginations import LimitOffsetObjectsPaginator


logger = logging.getLogger(__name__)


class GetRequestAbstractMixin(six.with_metaclass(abc.ABCMeta, object)):

    @property
    @abc.abstractmethod
    def request_object(self):
        """
        Get request object.

        :return: Request object.
        :rtype:

        """
        pass

    @property
    @abc.abstractmethod
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        pass


class GetSerializerMixin(GetRequestAbstractMixin):
    """
    Mixin for search serializer in handlers.

    """
    serializer_classes = {}

    def get_serializer(self, key):
        """
        Search serializer.

        :param str key: Key for search. Must be one from `in`, `out`.

        :return: Found serializer or None.
        :rtype: Optional[Type[rest_framework.serializers.Serializer]]

        """
        if key.lower() not in ('in', 'out'):
            return None
        serializers = self.serializer_classes.get(self.current_request_method.lower(), dict())

        if isinstance(serializers, dict):
            return serializers.get(key, serializers.get(key.lower(), serializers.get(key.upper(), None)))
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


# @check_attributes_on_none('response_class')
class GetResponseMixin(GetSerializerMixin):
    """
    Mixin for get Json response.

    """
    # Response class, for create Response.
    # Interface: data: Any(For JSON), status: int = response status.
    response_class = None

    # Paginator class for get pagination json
    pagination_class = LimitOffsetObjectsPaginator

    def __new__(cls, *args, **kwargs):
        res = super().__new__(cls, *args, **kwargs)
        # TODO: Not working
        if cls.response_class is None:
            raise AttributeError(
                'The attribute `response_class` in class `{}` not configure. '
                'Please check your class.'.format(cls)
            )
        return res

    def get_list_response(self, objs=None, is_serialized=True,
                          status_code=200,
                          *args, **kwargs):
        """
        Create and return response, object, for list objects.

        :param list objs: List object for return response.
        :param bool is_serialized: Is data serialization required?
        :param int status_code: Code server response.

        :return: Response object.

        """
        data = objs
        if is_serialized and objs is not None:
            data = self.get_response_serializer()(instance=objs, many=True).data

        paginate_data = self.pagination_class(objects=data).paginate(*args, **kwargs)

        return self.get_response(paginate_data, is_serialized=False, status_code=status_code)

    def get_response(self, obj=None, is_serialized=True,
                     status_code=200):
        """
        Create and return response object.

        :param object obj: Object for response body .
        :param bool is_serialized: Is data serialization required?
        :param int status_code: Code server response.

        :return: Response object.
        :rtype: aiohttp.web_response.Response

        """
        data = obj
        if is_serialized and obj is not None:
            data = self.get_response_serializer()(obj).data

        return self.response_class(data, status=status_code)
