"""
Ошибки в работе сериалайзеров.

"""


class ValidationError(Exception):
    """
    Ошибка валидаци.

    """
    # TODO: Эта ошибка, потом будет наследована от APIException и сможет обрабатываться error response handler-ром.
    default_detail = 'Неверные данные.'

    def __init__(self, detail=None, code=None):
        self.detail = detail
        self.code = code


class FieldSearchError(Exception):
    """
    Ошибка поиска филда.

    """
    pass
