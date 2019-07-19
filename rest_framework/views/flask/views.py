"""
Views for Flask.

"""
from flask import request, jsonify, make_response
from flask.views import View as _FlaskClassBaseView, MethodView as _FlaskClassBaseMethodView

from rest_framework.views.base import BaseApiView


def json_response(data, status=200, content_type='application/json'):
    """
    Json response for Flask.

    :param dict data: Data for response
    :param int status: Response status code.
    :param str content_type: Response Content-Type.

    :return: Response object.
    :rtype:

    """
    return make_response(jsonify(data), status, content_type=content_type)


class _BaseFlaskView(object):
    """
    Internal Flask base api view, for create base methods.

    """
    response_class = json_response

    @property
    def request_object(self):
        """
        Get request object.

        :return: Request object.
        :rtype:

        """
        return request

    @property
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        return request.method


class FlaskBaseApiView(_FlaskClassBaseView, _BaseFlaskView, BaseApiView):
    """
    Flask base api view.

    """
    @classmethod
    def as_view(cls, name, *class_args, **class_kwargs):
        """
        Converts the class into an actual view function that can be used
        with the routing system.  Internally this generates a function on the
        fly which will instantiate the :class:`View` on each request and call
        the :meth:`dispatch_request` method on it.

        The arguments passed to :meth:`as_view` are forwarded to the
        constructor of the class.

        """
        def view(*args, **kwargs):
            self = view.view_class(*class_args, **class_kwargs)
            if self.use_dispatch:
                return self._dispatch(self.dispatch_request, *args, **kwargs)
            return self.dispatch_request(*args, **kwargs)

        if cls.decorators:
            view.__name__ = name
            view.__module__ = cls.__module__
            for decorator in cls.decorators:
                view = decorator(view)

        # We attach the view class to the view function for two reasons:
        # first of all it allows us to easily figure out what class-based
        # view this thing came from, secondly it's also used for instantiating
        # the view class so you can actually replace it with something else
        # for testing purposes and debugging.
        view.view_class = cls
        view.__name__ = name
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.methods = cls.methods
        view.provide_automatic_options = cls.provide_automatic_options
        return view


class FlaskBaseMethodView(_FlaskClassBaseMethodView, _BaseFlaskView, BaseApiView):
    """
    Flask Method base api views.

    """
    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, self.current_request_method.lower(), None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if meth is None and self.current_request_method == 'HEAD':
            meth = getattr(self, 'get', None)

        assert meth is not None, 'Unimplemented method %r' % self.current_request_method
        if self.use_dispatch:
            return self._dispatch(meth, *args, **kwargs)
        return meth(*args, **kwargs)
