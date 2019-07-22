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
        super().__init__(*args, **kwargs)
        self.code = code

    def __str__(self):
        return 'rest_framework.serializers.exceptions.ValidationError(code={}, detail={}, code={})'.format(
            self.code, self.detail, self.status
        )
