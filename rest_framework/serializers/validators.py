"""
Валидаторы.

"""
from rest_framework.serializers.exceptions import ValidationError


class BaseValidator(object):
    """
    Базовый класс для валидатора.

    """
    message = ''

    def __init__(self, message=None):
        """
        Базовый класс для валидатора

        :param str message: Сообщение об ошибке.

        """
        self.message = message or self.message

    def __call__(self, value):
        """
        Сама валидация.

        :param object value: Объект для валидации.

        """
        raise NotImplementedError('`.__call__(self, value)` должен быть определен.')


class RequiredValidator(BaseValidator):
    """
    Валидатор на обязательность поля.

    """
    message = 'Это поле обязательное.'

    def __call__(self, value):
        """
        Валидируем.

        :param iter value: Объект, который валидируем.

        :raise ValidationError: Если не прошли валидацию.

        """
        if value is None:
            raise ValidationError(self.message)


class MinLengthValidator(BaseValidator):
    """
    Валидатор для минимальной длины.

    """
    message = 'Значение должно быть длиннее {min_length}.'

    def __init__(self, min_length, *args, **kwargs):
        """
        Создаем валидатор.

        :param int min_length: Минимальная длина.

        """
        super().__init__(*args, **kwargs)
        self.min_length = int(min_length)

    def __call__(self, value):
        """
        Валидируем.

        :param iter value: Объект, который валидируем.

        :raise ValidationError: Если не прошли валидацию.

        """
        if len(value) < self.min_length:
            raise ValidationError(self.message.format(dict(min_length=self.min_length)))


class MaxLengthValidator(BaseValidator):
    """
    Валидатор для максимальной длины.

    """
    message = 'Значение должно быть короче {max_length}.'

    def __init__(self, max_length, *args, **kwargs):
        """
        Создаем валидатор.

        :param int min_length: Максимальная длина.

        """
        super().__init__(*args, **kwargs)
        self.max_length = int(max_length)

    def __call__(self, value):
        """
        Валидируем.

        :param iter value: Объект, который валидируем.

        :raise ValidationError: Если не прошли валидацию.

        """
        if len(value) > self.max_length:
            raise ValidationError(self.message.format(dict(max_length=self.max_length)))


class MinValueValidator(BaseValidator):
    """
    Валидатор для минимального значения.

    """
    message = 'Значение должно быть больше или равно {min_value}.'

    def __init__(self, min_value, *args, **kwargs):
        """
        Создаем валидатор.

        :param object min_value: Минималное значение.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value

    def __call__(self, value):
        """
        Сама валидация.

        :param object value: Значение, которое нужно провалидировать.

        :raise ValidationError: Если валидацию не прошли.

        """
        if value < self.min_value:
            raise ValidationError(self.message.format(dict(min_value=self.min_value)))


class MaxValueValidator(BaseValidator):
    """
    Валидатор для максимального значения.

    """
    message = 'Значение должно быть меньше или равно {max_value}.'

    def __init__(self, max_value, *args, **kwargs):
        """
        Создаем валидатор.

        :param object max_value: Максимальное значение.

        """
        super().__init__(*args, **kwargs)
        self.max_value = max_value

    def __call__(self, value):
        """
        Сама валидация.

        :param object value: Значение, которое нужно провалидировать.

        :raise ValidationError: Если валидацию не прошли.

        """
        if value > self.max_value:
            raise ValidationError(self.message.format(dict(max_value=self.max_value)))
