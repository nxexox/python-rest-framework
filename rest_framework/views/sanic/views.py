"""
Views for aiohttp.

"""

from sanic import response
from sanic.views import (
    HTTPMethodView as _SanicHTTPMethodView,
    CompositionView as _SanicCompositionView
)

from rest_framework.views.base import BaseApiView


json_response = response.json


class _BaseSanicView(object):
    """
    Internal Sanic base api view, for create base methods.

    """
    response_class = response.json

    @property
    def request_object(self):
        """
        Get request object.

        :return: Request object.
        :rtype:

        """
        return self._request

    @property
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        return self._request.method


class SanicApiMethodView(_SanicHTTPMethodView, BaseApiView, _BaseSanicView):
    """
    Sanic base API methods view.

    """
    def dispatch_request(self, request, *args, **kwargs):
        handler = getattr(self, request.method.lower(), None)
        self._request = request

        if self.use_dispatch:
            return self._dispatch(handler, request, *args, **kwargs)
        return handler(request, *args, **kwargs)


class SanicApiCompositionView(_SanicCompositionView, BaseApiView, _BaseSanicView):
    """
    Sanic base API methods composition view.

    """
    def __call__(self, request, *args, **kwargs):
        handler = self.handlers.get(
            request.method.lower(), self.handlers.get(
                request.method.upper(), self.handlers[request.method]
            )
        )
        self._request = request

        if self.use_dispatch:
            return self._dispatch(handler, request, *args, **kwargs)
        return handler(request, *args, **kwargs)
