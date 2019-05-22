"""
Errors for serializers.

"""
from rest_framework.exceptions import ApiException


class ValidationError(ApiException):
    """
    Validation error.

    """
    default_detail = 'Invalid input.'

    def __init__(self, code=None, *args, **kwargs):
        """
        Validation error.

        :param str code: Code, for check error type and get current error message.

        """
        self.code = code
