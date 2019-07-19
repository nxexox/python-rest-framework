"""
Generics for aiohttp views.

"""
from rest_framework.views.aiohttp.views import AioHTTPApiView
from rest_framework.views.mixins import (
    GetSerializerMixin, GetResponseMixin
)
from rest_framework.views.aiohttp.mixins import GetValidJsonMixin


class GetSerializerApiGenericView(AioHTTPApiView, GetSerializerMixin):
    """
    Generic Api view for GetSerializer methods.

    """
    pass


class GetResponseApiGenericView(AioHTTPApiView, GetResponseMixin):
    """
    Generic Api view for GetResponse methods.

    """
    pass


class GetValidJsonApiGenericView(AioHTTPApiView, GetValidJsonMixin):
    """
    Generic APi view got GetValidJson methods.

    """
    pass


class ApiGenericView(AioHTTPApiView, GetResponseMixin, GetSerializerMixin, GetValidJsonMixin):
    """
    Generic Api view for GetResponse, GetSerializer, GetValidJsonMixin methods.

    """
    pass
