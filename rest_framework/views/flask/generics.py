"""
Generics for Flask views.

"""
from rest_framework.views.flask.views import FlaskBaseApiView, FlaskBaseMethodView
from rest_framework.views.mixins import (
    GetSerializerMixin, GetResponseMixin
)
from rest_framework.views.flask.mixins import GetValidJsonMixin


class GetSerializerApiGenericView(FlaskBaseApiView, GetSerializerMixin):
    """
    Generic Api view for GetSerializer methods.

    """
    pass


class GetResponseApiGenericView(FlaskBaseApiView, GetResponseMixin):
    """
    Generic Api view for GetResponse methods.

    """
    pass


class GetValidJsonApiGenericView(FlaskBaseApiView, GetValidJsonMixin):
    """
    Generic APi view for GetValidJsonMixin methods.

    """
    pass


class ApiGenericView(FlaskBaseApiView, GetResponseMixin, GetValidJsonMixin, GetSerializerMixin):
    """
    Generic Api view for GetResponse, GetSerializer, GetValidJsonMixin methods.

    """
    pass


class GetSerializerApiGenericMethodView(FlaskBaseMethodView, GetSerializerMixin):
    """
    Generic Api method view for GetSerializer methods.

    """
    pass


class GetResponseApiGenericMethodView(FlaskBaseMethodView, GetResponseMixin):
    """
    Generic Api method view for GetResponse methods.

    """
    pass


class GetValidJsonApiGenericMethodView(FlaskBaseMethodView, GetValidJsonMixin):
    """
    Generic Api method view for GetValidJsonMixin methods.

    """
    pass


class ApiGenericMethodView(FlaskBaseMethodView, GetResponseMixin, GetValidJsonMixin, GetSerializerMixin):
    """
    Generic Api method view for GetResponse, GetSerializer, GetValidJsonMixin methods.

    """
    pass
