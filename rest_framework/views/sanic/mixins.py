"""
Mixins for views AioHttp.

"""
try:
    from json.decoder import JSONDecodeError
except (AttributeError, ImportError):
    JSONDecodeError = ValueError

from rest_framework.views.mixins import GetSerializerMixin
from rest_framework.serializers.exceptions import ValidationError


class GetValidJsonMixin(GetSerializerMixin):
    """
    Mixin for method get_valid json.

    """
    def get_valid_json(self, parse_query=False, raise_exception=True):
        """
        Make, Validate and return JSON from request BODY.

        :param bool parse_query: Parse query or only body?
        :param bool raise_exception: Raise exception if body not parse?

        :return: Validated data from request BODY.
        :rtype: Optional[dict]

        """
        # Get request query
        data = self.request_object.args.copy() if parse_query else {}
        # Get request body
        try:
            data.update(self.request_object.json)
        except JSONDecodeError:
            if raise_exception:
                raise ValidationError('Not valid json.')

        # Validate body request.
        serializer = self.get_request_serializer()
        if serializer is None:
            return None
        serializer = serializer(data=data)
        serializer.is_valid(raise_exception=True)

        return serializer.validated_data
