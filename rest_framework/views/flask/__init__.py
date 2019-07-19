import warnings

try:
    from .views import FlaskBaseApiView, FlaskBaseMethodView, json_response
    from .generics import (
        GetResponseApiGenericView, GetSerializerApiGenericView, ApiGenericView,
        GetSerializerApiGenericMethodView, GetResponseApiGenericMethodView, ApiGenericMethodView
    )
    from .mixins import GetValidJsonMixin
    __all__ = [
        FlaskBaseApiView, FlaskBaseMethodView,
        GetResponseApiGenericView, GetSerializerApiGenericView, ApiGenericView,
        GetSerializerApiGenericMethodView, GetResponseApiGenericMethodView, ApiGenericMethodView,
        GetValidJsonMixin,
        json_response
    ]
except (ImportError, AttributeError):
    warnings.warn(
        'Cannot import Flask. '
        'Please check that you have a version for Flask python-rest-framework[flask] '
        'installed and that Flask is installed.',
        ImportWarning
    )
    __all__ = []
