"""
Errors for serializers.

"""


class ValidationError(Exception):
    """
    Validation error.

    """
    # TODO: This error will then be inherited from an APIException and will be able to handle the error response handler.
    default_detail = 'Invalid input.'

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code
