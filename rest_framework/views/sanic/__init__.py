import warnings

try:
    from .views import SanicApiMethodView, SanicApiCompositionView, json_response
    from .generics import (
        GetResponseApiGenericMethodView, GetSerializerApiGenericMethodView, GetValidJsonApiGenericMethodView,
        ApiGenericMethodView,
        GetResponseApiGenericCompositionView, GetSerializerApiGenericCompositionView,
        GetValidJsonApiGenericCompositionView, SanicApiCompositionView
    )
    from .mixins import GetValidJsonMixin
    __all__ = [
        SanicApiMethodView, SanicApiCompositionView,

        GetResponseApiGenericMethodView, GetSerializerApiGenericMethodView, GetValidJsonApiGenericMethodView,
        ApiGenericMethodView,
        GetResponseApiGenericCompositionView, GetSerializerApiGenericCompositionView,
        GetValidJsonApiGenericCompositionView, SanicApiCompositionView,

        GetValidJsonMixin,
        json_response
    ]
except (ImportError, AttributeError):
    warnings.warn(
        'Cannot import sanic. '
        'Please check that you have a version for sanic python-rest-framework[sanic] '
        'installed and that sanic is installed.',
        ImportWarning
    )
    __all__ = []
