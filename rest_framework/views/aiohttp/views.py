"""
Views for aiohttp.

"""
import asyncio

from aiohttp.hdrs import METH_ALL

from rest_framework.views import BaseApiView, GetSerializerAbstractMixin


class AioHTTPApiView(BaseApiView, GetSerializerAbstractMixin):
    """
    AioHTTP base API view.

    """
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

        response = await self.dispatch(method)

        return response
