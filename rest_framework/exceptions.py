"""
Errors.

"""


class SkipError(Exception):
    """
    An error that is worth missing.

    """
    pass


class ApiException(Exception):
    """
    Exception for raise in api.

    """
    def __init__(self, detail=None, status=400):
        """
        Exception for raise in api.

        :param Optional[dict, str, int, float, list] detail: Body request data. Valid json objects.
        :param int status: Response status code.

        """
        self.detail = detail
        self.status = status
