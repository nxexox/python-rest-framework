"""
Generics for Flask views.

"""
from rest_framework.views.sanic.views import SanicApiMethodView, SanicApiCompositionView
from rest_framework.views.mixins import (
    GetSerializerMixin, GetResponseMixin
)
from rest_framework.views.sanic.mixins import GetValidJsonMixin


class GetSerializerApiGenericMethodView(SanicApiMethodView, GetSerializerMixin):
    """
    Generic Api method view for GetSerializer methods.

    """
    pass


class GetResponseApiGenericMethodView(SanicApiMethodView, GetResponseMixin):
    """
    Generic Api method view for GetResponse methods.

    """
    pass


class GetValidJsonApiGenericMethodView(SanicApiMethodView, GetValidJsonMixin):
    """
    Generic Api method view for GetValidJsonMixin methods.

    """
    pass


class ApiGenericMethodView(SanicApiMethodView, GetResponseMixin, GetSerializerMixin, GetValidJsonMixin):
    """
    Generic Api method view for GetResponse, GetSerializer, GetValidJsonMixin methods.

    """
    pass


class GetSerializerApiGenericCompositionView(SanicApiCompositionView, GetSerializerMixin):
    """
    Generic Api composition view for GetSerializer methods.

    """
    pass


class GetResponseApiGenericCompositionView(SanicApiCompositionView, GetResponseMixin):
    """
    Generic Api composition view for GetResponse methods.

    """
    pass


class GetValidJsonApiGenericCompositionView(SanicApiCompositionView, GetValidJsonMixin):
    """
    Generic APi composition view for GetValidJsonMixin methods.

    """
    pass


class ApiGenericCompositionView(SanicApiCompositionView, GetResponseMixin, GetSerializerMixin, GetValidJsonMixin):
    """
    Generic Api composition view for GetResponse, GetSerializer, GetValidJsonMixin methods.

    """
    pass
