"""
Views for aiohttp.

"""
import asyncio

from aiohttp.hdrs import METH_ALL
from aiohttp.web import (
    View as AioHttpClassBaseView,
    json_response
)

from rest_framework.views.base import BaseApiView
from rest_framework.exceptions import ApiException


class AioHTTPApiView(AioHttpClassBaseView, BaseApiView):
    """
    AioHTTP base API view.

    """
    response_class = json_response

    @property
    def request_object(self):
        """
        Get request object.

        :return: Request object.
        :rtype:

        """
        return self.request

    @property
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        return self.request.method

    @asyncio.coroutine
    def _iter(self):
        """
        Iter for request handler.

        """
        if self.request.method not in METH_ALL:
            self._raise_allowed_methods()

        method = getattr(self, self.request.method.lower(), None)

        if method is None:
            self._raise_allowed_methods()

        if self.use_dispatch:
            response = yield from self._dispatch(method)
        else:
            response = yield from method()

        return response

    @asyncio.coroutine
    def _dispatch(self, method, *args, **kwargs):
        """
        Code after, before call request handler.

        :param function method: Method handler for call.

        """
        try:
            result = yield from method()
            return result
        except ApiException as e:
            # TODO: Not security. e.detail maybe anything
            return self.response_class.__func__(detail={'errors': e.detail}, status=e.status or 400)
