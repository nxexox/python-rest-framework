"""
Validators.

"""
from rest_framework.serializers.exceptions import ValidationError


class BaseValidator(object):
    """
    base class for validator.

    """
    message = ''

    def __init__(self, message=None):
        """
        Base class for validator.

        :param str message: Error message.

        """
        self.message = message or self.message

    def __call__(self, value):
        """
        Validation.

        :param object value: Object for validation.

        """
        raise NotImplementedError('`.__call__(self, value)` must be implemented.')


class RequiredValidator(BaseValidator):
    """
    Validator on required field.

    """
    message = 'This field is required.'

    def __call__(self, value):
        """
        Validation.

        :param iter value: Object for validation.

        :raise ValidationError: If not valid data.

        """
        if value is None:
            raise ValidationError(self.message)


class MinLengthValidator(BaseValidator):
    """
    Validator for minimum length.

    """
    message = 'The value must be longer than {min_length}.'

    def __init__(self, min_length, *args, **kwargs):
        """
        Validator.

        :param int min_length: Minimum length.

        """
        super().__init__(*args, **kwargs)
        self.min_length = int(min_length)

    def __call__(self, value):
        """
        Validation.

        :param iter value: Object for validation.

        :raise ValidationError: If not valid data.

        """
        if len(value) < self.min_length:
            raise ValidationError(self.message.format(dict(min_length=self.min_length)))


class MaxLengthValidator(BaseValidator):
    """
    Validator for maximum length.

    """
    message = 'The value must be shorter than {max_length}.'

    def __init__(self, max_length, *args, **kwargs):
        """
        Validator for maximum length.

        :param int min_length: Maximum length.

        """
        super().__init__(*args, **kwargs)
        self.max_length = int(max_length)

    def __call__(self, value):
        """
        Validation.

        :param iter value: Object for validation.

        :raise ValidationError: If not valid data.

        """
        if len(value) > self.max_length:
            raise ValidationError(self.message.format(dict(max_length=self.max_length)))


class MinValueValidator(BaseValidator):
    """
    Validator for minimal value.

    """
    message = 'The value must be greater than or equal to {min_value}.'

    def __init__(self, min_value, *args, **kwargs):
        """
        Validator for minimal value.

        :param object min_value: Minimum value.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value

    def __call__(self, value):
        """
        Validation.

        :param object value: Value for validation.

        :raise ValidationError: If not valid data.

        """
        if value < self.min_value:
            raise ValidationError(self.message.format(dict(min_value=self.min_value)))


class MaxValueValidator(BaseValidator):
    """
    Validator for maximum value.

    """
    message = 'The value must be less than or equal to {max_value}.'

    def __init__(self, max_value, *args, **kwargs):
        """
        Validator for maximum value.

        :param object max_value: Maximum value.

        """
        super().__init__(*args, **kwargs)
        self.max_value = max_value

    def __call__(self, value):
        """
        Validation.

        :param object value: Value for validation.

        :raise ValidationError: If not valid data.

        """
        if value > self.max_value:
            raise ValidationError(self.message.format(dict(max_value=self.max_value)))
