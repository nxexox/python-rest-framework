import warnings

try:
    from .views import AioHTTPApiView, json_response
    from .generics import GetResponseApiGenericView, GetSerializerApiGenericView, ApiGenericView
    from .mixins import GetValidJsonMixin
    __all__ = [
        AioHTTPApiView,
        GetResponseApiGenericView, GetSerializerApiGenericView, ApiGenericView,
        GetValidJsonMixin,
        json_response
    ]
except (ImportError, AttributeError):
    warnings.warn(
        'Cannot import aiohttp. '
        'Please check that you have a version for aiohttp python-rest-framework[aiohttp] '
        'installed and that aiohttp is installed.',
        ImportWarning
    )
    __all__ = []
