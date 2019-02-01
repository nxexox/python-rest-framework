"""
Fields for serializers.

"""
import re
try:
    from typing import Mapping
except ImportError:
    from collections import Mapping
import datetime
import json

try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError

import six

from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError
from rest_framework.utils import html
from rest_framework.serializers.validators import (
    RequiredValidator, MaxLengthValidator, MinLengthValidator, MaxValueValidator, MinValueValidator
)

MISSING_ERROR_MESSAGE = (
    'Raise `ValidationError` exception for `{class_name}`, '
    'not found key `{key}` in dict `error_messages`.'
)  # Default error message, for situation not error key in error_messages dict.
# Default formats for parse, transformed datetime.
DEFAULT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_TIME_FORMAT = '%H:%M:%S'
DEFAULT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
DEFAULT_INPUT_DATE_FORMAT = '%Y-%m-%d'
DEFAULT_INPUT_TIME_FORMAT = '%H:%M:%S'
DEFAULT_INPUT_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def get_attribute(obj, attr_name):
    """
    Return object attribute. Can work with dictionaries.

    :param object obj: Object for search attribute.
    :param str attr_name: Attribute name.

    :return: Found attribute or exception.
    :rtype: object

    :raise AttributeError: If attribute not found.

    """
    # Search attribute.
    if isinstance(obj, Mapping):
        attr = obj[attr_name]
    else:
        attr = getattr(obj, attr_name)

    # Return.
    return attr


class Field(object):
    """
    Base field.

    """
    default_error_messages = {
        'required': 'This field is required.',
        'null': 'This field cannot be null.'
    }
    default_validators = []  # Default validators for field.

    def __init__(self, required=True, default=None, label=None, validators=None, error_messages=None):
        """
        Base field.

        :param bool required: This is required field?
        :param object default: Default value. If set, then the field is optional.
        :param str label: Field name.
        :param list validators: Validators for field.
        :param dict error_messages: Dictionary with custom error description.

        """
        self.label = label
        self.default = default
        self.required = bool(required) if self.default is None else False
        # Added validator for check on required field.
        self._src_validators = validators
        self._validators = ([RequiredValidator()] if self.required else []) + (validators or [])[:]

        # Make errors dict.
        messages = {}
        self._src_messages = messages
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages
        )

    def bind(self, field_name, parent):
        """
        Initialization field name and parent instance .
        Called when a field is added to an instance of the parent..

        :param str field_name: Field name.
        :param Serializer parent: Serializer class on which the field is located.

        """
        self.field_name = field_name
        self.parent = parent

        # We put the label ourselves if it's not there.
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()

    @property
    def validators(self):
        """
        :return: List validators for this field.
        :rtype: list

        """
        if not hasattr(self, '_validators'):
            self._validators = self.get_validators()
        return self._validators

    @validators.setter
    def validators(self, validators):
        """
        We give access to change the list of validators.

        :param list validators: New list validators for this field.

        """
        self._validators = validators

    def get_validators(self):
        """
        Return default validators.
        Used to generate a list of validators if they are not explicitly defined.

        :return: List default validators.
        :rtype: list

        """
        return self.default_validators[:]

    def fail(self, key, **kwargs):
        """
        We throw a normal error if something went wrong during data processing.

        :param str key: Error type. Key for dict `self.default_error_messages`.
        :param kwargs: Data to format error message.

        :raise AssertionError: If you have not found the key in the `self.error_messages`.
        :raise ValidationError: If you find the key in the `self.error_messages`.

        """
        # Trying to get an error message.
        try:
            msg = self.error_messages[key]
        except KeyError:
            # If we could not talk about it, I use a general message.
            class_name = self.__class__.__name__
            msg = MISSING_ERROR_MESSAGE.format(class_name=class_name, key=key)
            raise AssertionError(msg)

        # Format the message and throw an error.
        message_string = msg.format(**kwargs)
        raise ValidationError(message_string, code=key)

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param object data: Data for transformation.

        :return: Transformed data.
        :rtype: object

        """
        raise NotImplementedError('`to_internal_value()` must be implemented.')

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param object value: The object to transformation.

        :return: Transformed data.
        :rtype: object

        """
        raise NotImplementedError('`to_representation()` must be implemented.')

    def get_default(self):
        """
        Return default value.
        If necessary, initially call the callable object to get the default value..

        :return: Default value.
        :rtype: object

        """
        if callable(self.default):
            return self.default()
        return self.default

    def _get_field_name(self):
        """
        Get field name for search attribute on object.

        :return: Field name for search attribute.
        :rtype: str

        """
        return self.field_name

    def _get_attribute(self, instance):
        """
        Searches for and returns an attribute on an object..

        :return: Object attribute value.
        :rtype: object

        :raise SkipError: If you could not find the field and the field is required.
        :raise Exception: If an error occurred during the search.

        """
        return get_attribute(instance, self._get_field_name())

    def get_attribute(self, instance):
        """
        Searches for and returns an attribute on an object..

        :return: Object attribute value.
        :rtype: object

        :raise SkipError: If you could not find the field and the field is required.
        :raise Exception: If an error occurred during the search.

        """
        try:
            # Trying to get an attribute.
            return self._get_attribute(instance)
        except (KeyError, AttributeError) as e:
            # If there is a default value, then it.
            if self.default is not None:
                return self.get_default()
            # If there is no default and the field is required, we swear.
            if self.required:
                raise SkipError(self.error_messages['required'])

            # Otherwise, we report this incident to the developer..
            msg = (
                'Got {exc_type} when attempting to get a value for field '
                '`{field}` on serializer `{serializer}`.\nThe serializer '
                'field might by named incorrectly and not match '
                'any attribute or key on the `{instance}` object.\n'
                'Original exception text was: {exc}.'.format(
                    exc_type=type(e).__name__,
                    field=self.field_name,
                    serializer=self.parent.__name__,
                    instance=instance.__class__.__name__,
                    exc=e
                )
            )
            raise type(e)(msg)

    def validate_empty_values(self, data):
        """
        Check if the value is empty.

        :param object data: Data for check.

        :return: The result of check, and current data.
                 If there is a default value and nothing is passed, returns the default.
                 Tuple: (is None, actual data)
        :rtype: tuple

        :raise ValidationError: If validation on an empty field did not pass.

        """
        # Process.
        is_empty, data = data is None, data if data is not None else self.default

        # Validating.
        if is_empty and not self.required:
            return is_empty, data

        # If empty and not necessary, then there is nothing to validate and transformed.
        if is_empty:
            raise ValidationError(self.error_messages['required'])

        # Return.
        return is_empty, data

    def run_validation(self, data):
        """
        Starts data transformed, then validation..

        :param object data: Data worth checking, transformed, etc..

        :return: Transformed Validated Data.
        :rtype: object

        :raise ValidationError: If the field failed validation.

        """
        # First, we validate to be bound.
        is_empty, data = self.validate_empty_values(data)

        # If empty data and field not required.
        if is_empty and not self.required:
            return data

        # Process raw data.
        value = self.to_internal_value(data)
        # Run validators.
        self.run_validators(value)

        return value

    def run_validators(self, value):
        """
        Validates all field validators.

        :param object value: Data for validation.

        :raise ValidationError: If validation fails.

        """
        errors = []

        for validator in self.validators or []:
            try:
                # Run each validator.
                validator(value)
            except ValidationError as e:
                errors.append(e.detail)

        # Check on errors.
        if errors:
            raise ValidationError(errors)


class CharField(Field):
    """
    Field for text.

    """
    default_error_messages = {
        'invalid': 'Not a valid string.',
        'blank': 'This field may not be blank.',
        'min_length': 'Ensure this field has at least {min_length} characters.',
        'max_length': 'Ensure this field has no more than {max_length} characters.'
    }

    def __init__(self, min_length=None, max_length=None, trim_whitespace=False, allow_blank=True, *args, **kwargs):
        """
        Field for text.

        :param int min_length: Minimum length string.
        :param int max_length: Maximum length string.
        :param bool trim_whitespace: Whether to trim spaces at the beginning and end of a line?
        :param bool allow_blank: Allow empty string?

        """
        super().__init__(*args, **kwargs)
        self.max_length = max_length if max_length is None else int(max_length)
        self.min_length = min_length if min_length is None else int(min_length)
        self.trim_whitespace = trim_whitespace
        self.allow_blank = allow_blank

        # Added validators.
        if self.max_length is not None:
            message = self.error_messages['max_length'].format(max_length=self.max_length)
            self.validators.append(MaxLengthValidator(max_length, message=message))
        if self.min_length is not None:
            message = self.error_messages['min_length'].format(min_length=self.min_length)
            self.validators.append(MinLengthValidator(self.min_length, message=message))

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            min_length=self.min_length, max_length=self.max_length,
            trim_whitespace=self.trim_whitespace, allow_blank=self.allow_blank
        )

    def run_validation(self, data=None):
        """
        We check for an empty string here, so that it does not fall into subclasses in `.to_internal_value ()`.

        :param object data: Data for validation.

        :return: Transformed Validated Data.
        :rtype: str

        """
        if data == '' or (self.trim_whitespace and six.text_type(data).strip() == ''):
            if not self.allow_blank:
                self.fail('blank')
            return ''
        return super(CharField, self).run_validation(data)

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: str

        :raise ValidationError: If not valid data.

        """
        # We skip numbers as strings, but bool as strings seems to be a developer error.
        if isinstance(data, bool) or not isinstance(data, six.string_types + six.integer_types + (float,)):
            self.fail('invalid')
        return six.text_type(data)

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param str value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        return six.text_type(value)


class IntegerField(Field):
    """
    Field for integer number.

    """
    default_error_messages = {
        'invalid': 'A valid integer is required.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000  # We limit the maximum length.
    re_decimal = re.compile(r'\.0*\s*$')  # '1.0' is int, is not int '1.2'

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        """
        Field for integer number.

        :param int min_value: Minimum value.
        :param int max_value: Maximum value.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value if min_value is None else int(min_value)
        self.max_value = max_value if max_value is None else int(max_value)

        # Added validators.
        if self.min_value is not None:
            message = self.error_messages['min_value'].format(min_value=self.min_value)
            self.validators.append(MinValueValidator(self.min_value, message=message))
        if self.max_value is not None:
            message = self.error_messages['max_value'].format(max_value=self.max_value)
            self.validators.append(MaxValueValidator(self.max_value, message=message))

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            min_value=self.min_value, max_value=self.max_value
        )

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param Union[str, int, float] data: Data for transformation.

        :return: Transformed data.
        :rtype: int

        :raise ValidationError: Id not valid data.

        """
        # We look, do not want us to score a memory?
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            data = int(self.re_decimal.sub('', str(data)))
        except (ValueError, TypeError):
            self.fail('invalid')
        return data

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param int value: The object to transformation.

        :return: Transformed data.
        :rtype: int

        """
        return int(value)


class FloatField(Field):
    """
    Field for floating number.

    """
    default_error_messages = {
        'invalid': 'A valid integer is required.',
        'min_value': 'Ensure this value is greater than or equal to {min_value}.',
        'max_value': 'Ensure this value is less than or equal to {max_value}.',
        'max_string_length': 'String value too large.'
    }
    MAX_STRING_LENGTH = 1000  # We limit the maximum length.

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        """
        Field for floating number.

        :param float min_value: Minimum value.
        :param float max_value: Maximum value.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value if min_value is None else float(min_value)
        self.max_value = max_value if max_value is None else float(max_value)

        # Added validators.
        if self.min_value is not None:
            message = self.error_messages['min_value'].format(min_value=self.min_value)
            self.validators.append(MinValueValidator(self.min_value, message=message))
        if self.max_value is not None:
            message = self.error_messages['max_value'].format(max_value=self.max_value)
            self.validators.append(MaxValueValidator(self.max_value, message=message))

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            min_value=self.min_value, max_value=self.max_value
        )

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param Union[str, int, float] data: Data for transformation.

        :return: Transformed data.
        :rtype: float

        :raise ValidationError: If not valid data.

        """
        # We look, do not want us to score a memory?
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            return float(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param float value: The object to transformation.

        :return: Transformed data.
        :rtype: float

        """
        return float(value)


class BooleanField(Field):
    """
    Field for boolean type.

    """
    default_error_messages = {
        'invalid': '"{input}" must be a valid boolean type.'
    }
    TRUE_VALUES = {
        't', 'T',
        'y', 'Y', 'yes', 'YES', 'Yes',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    }  # Dict with True options.
    FALSE_VALUES = {
        'f', 'F', 'n',
        'N', 'no', 'NO', 'No',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    }  # Dictionary with False options.
    NULL_VALUES = {'n', 'N', 'null', 'Null', 'NULL', '', None}  # Dictionary with NULL options.

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param Union[str, int, float, bool] data: Data for transformation.

        :return: Transformed data.
        :rtype: bool

        :raise ValidationError: If not valid data.

        """
        try:
            if data in self.TRUE_VALUES:
                return True
            elif data in self.FALSE_VALUES:
                return False
            elif data in self.NULL_VALUES:
                return None
        except TypeError:  # If the non-hash type came.
            pass
        self.fail('invalid', input=data)

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param Union[str, int, float, bool] value: The object to transformation.

        :return: Transformed data.
        :rtype: bool

        """
        # First we look for in the match table.
        if value in self.NULL_VALUES:
            return None
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        # If not found, try to transform.
        return bool(value)


class _UnvalidatedField(Field):
    """
    Field, which is forwarding data as is.

    """
    def __init__(self, *args, **kwargs):
        """
        Field, which is forwarding data as is

        """
        super(_UnvalidatedField, self).__init__(*args, **kwargs)
        self.allow_blank = True

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param object data: Data for transformation.

        :return: Source value.
        :rtype: object

        :raise ValidationError: If not valid data.

        """
        return data

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param object value: The object to transformation.

        :return: Source value.
        :rtype: object

        """
        return value


class ListField(Field):
    """
    Field for list objects.

    """
    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'empty': 'This list may not be empty.',
        'min_length': 'Ensure this field has at least {min_length} elements.',
        'max_length': 'Ensure this field has no more than {max_length} elements.'
    }
    child = _UnvalidatedField()

    def __init__(self, child=None, min_length=None, max_length=None, allow_empty=False, *args, **kwargs):
        """
        Field for list objects.

        :param rest_framework.serializers.Field child: Field describing the type of array elements.
        :param int min_length: Minimum length list.
        :param int max_length: Maximum length list.
        :param bool allow_empty: Allow empty array?

        """
        super().__init__(*args, **kwargs)
        self.child = child or self.child
        self.min_length = min_length if min_length is None else int(min_length)
        self.max_length = max_length if max_length is None else int(max_length)
        self.allow_empty = bool(allow_empty)

        # Check field `child`.
        if all((not isinstance(child, Field), not isinstance(self.child, Field))):
            raise ValueError('`child=` or `self.child` must be Field.')

        self.child.bind(field_name='', parent=self)  # Bind child field.

        # Added validators.
        if self.max_length is not None:
            message = self.error_messages['max_length'].format(max_length=self.max_length)
            self.validators.append(MaxLengthValidator(max_length, message=message))
        if self.min_length is not None:
            message = self.error_messages['min_length'].format(min_length=self.min_length)
            self.validators.append(MinLengthValidator(self.min_length, message=message))

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            child=self.child, min_length=self.min_length, max_length=self.max_length,
            allow_empty=self.allow_empty
        )

    def to_internal_value(self, data):
        """
        Data transformation to python list object.

        :param iter data: Data for transformation.

        :return: Transformed data.
        :rtype: list

        :raise ValidationError: If not valid data.

        """
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        if any((isinstance(data, type('')), isinstance(data, Mapping), not hasattr(data, '__iter__'))):
            self.fail('not_a_list', input_type=type(data).__name__)

        if not self.allow_empty and len(data) == 0:
            self.fail('empty')

        return [self.child.run_validation(item) for item in data]

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON list object.

        :param iter value: The object to transformation.

        :return: Transformed data.
        :rtype: list

        """
        return [self.child.to_representation(item) if item is not None else None for item in (value or [])]


class DateField(Field):
    """
    Field for date object.

    """
    default_error_messages = {
        'invalid': 'Date has wrong format. Use one of these formats instead: {format}.',
        'datetime': 'Expected a date but got a datetime.',
    }
    datetime_parser = datetime.datetime.strptime
    format = DEFAULT_DATE_FORMAT
    input_format = DEFAULT_INPUT_DATE_FORMAT

    def __init__(self, format=None, input_format=None, *args, **kwargs):
        """
        Field for date object.

        :param str format: Format for parse string date.
        :param str input_format: Format for transformed object to string.

        """
        if format is not None:
            self.format = format
        if input_format is not None:
            self.input_format = input_format
        super().__init__(*args, **kwargs)

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            format=getattr(self, 'format'), input_format=getattr(self, 'input_format')
        )

    def to_internal_value(self, data):
        """
        Data transformation to python datetime object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: datetime.date

        :raise ValidationError: If not valid data.

        """
        # Get the format.
        input_format = getattr(self, 'input_format', DEFAULT_INPUT_DATE_FORMAT)

        # Check on the datetime object.
        if isinstance(data, datetime.datetime):
            self.fail('datetime')

        # Check on the date object.
        if isinstance(data, datetime.date):
            return data

        # Parsed data value from string.
        try:
            parsed = self.datetime_parser(data, input_format)
        except (ValueError, TypeError):
            pass
        else:
            # Return value.
            return parsed.date()

        # Throw exception.
        self.fail('invalid', format=data)

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON date object.

        :param datetime.date value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        # Check on the empty.
        if not value:
            return None

        # Check format and value type.
        output_format = getattr(self, 'format', DEFAULT_DATE_FORMAT)
        if output_format is None or isinstance(value, six.string_types):
            return value

        # Applying a `DateField` to a datetime value is almost always
        # not a sensible thing to do, as it means naively dropping
        # any explicit or implicit timezone info.
        assert not isinstance(value, datetime.datetime), (
            'Expected a `date`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        return value.strftime(output_format)


class TimeField(Field):
    """
    Field for time object.

    """
    default_error_messages = {
        'invalid': 'Time has wrong format. Use one of these formats instead: {format}.',
    }
    datetime_parser = datetime.datetime.strptime
    format = DEFAULT_TIME_FORMAT
    input_format = DEFAULT_INPUT_TIME_FORMAT

    def __init__(self, format=None, input_format=None, *args, **kwargs):
        """
        Field for time object.

        :param str format: Format for parse string time.
        :param str input_format: Format for transformed object to string.

        """
        if format is not None:
            self.format = format
        if input_format is not None:
            self.input_format = input_format
        super().__init__(*args, **kwargs)

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            format=getattr(self, 'format', None), input_format=getattr(self, 'input_format')
        )

    def to_internal_value(self, data):
        """
        Data transformation to python datetime object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: datetime.time

        :raise ValidationError: If not valid data.

        """
        # Get the format.
        input_format = getattr(self, 'input_format', DEFAULT_INPUT_TIME_FORMAT)

        # Check on the date object.
        if isinstance(data, datetime.time):
            return data

        # Parsed data value from string.
        try:
            parsed = self.datetime_parser(data, input_format)
        except (ValueError, TypeError):
            pass
        else:
            # Return value.
            return parsed.time()

        # Throw exception.
        self.fail('invalid', format=data)

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON time object.

        :param datetime.time value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        # Check on None.
        if value in (None, ''):
            return None

        # Check format and value type.
        output_format = getattr(self, 'format', DEFAULT_TIME_FORMAT)
        if output_format is None or isinstance(value, six.string_types):
            return value

        # Applying a `TimeField` to a datetime value is almost always
        # not a sensible thing to do, as it means naively dropping
        # any explicit or implicit timezone info.
        assert not isinstance(value, datetime.datetime), (
            'Expected a `time`, but got a `datetime`. Refusing to coerce, '
            'as this may mean losing timezone information. Use a custom '
            'read-only field and deal with timezone issues explicitly.'
        )

        return value.strftime(output_format)


class DateTimeField(Field):
    """
    Field for datetime.

    """
    default_error_messages = {
        'invalid': 'Datetime has wrong format. Use one of these formats instead: {format}.',
        'date': 'Expected a datetime but got a date.',
    }
    datetime_parser = datetime.datetime.strptime
    format = DEFAULT_DATETIME_FORMAT
    input_format = DEFAULT_INPUT_DATETIME_FORMAT

    def __init__(self, format=None, input_format=None, *args, **kwargs):
        """
        Field for time object.

        :param str format: Format for parse string time.
        :param str input_format: Format for transformed object to string.

        """
        if format is not None:
            self.format = format
        if input_format is not None:
            self.input_format = input_format

        super(DateTimeField, self).__init__(*args, **kwargs)

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            format=getattr(self, 'format'), input_format=getattr(self, 'input_format')
        )

    def to_internal_value(self, data):
        """
        Data transformation to python datetime object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: datetime.datetime

        :raise ValidationError: If not valid data.

        """
        # Get the format.
        input_format = getattr(self, 'input_format', DEFAULT_INPUT_DATETIME_FORMAT)

        # Check ot the data ot datetime object.
        if isinstance(data, datetime.date):
            if not isinstance(data, datetime.datetime):
                self.fail('date')
            else:
                return data

        # Parsed and return data.
        try:
            return self.datetime_parser(data, input_format)
        except (ValueError, TypeError):
            pass

        # Throw error.
        self.fail('invalid', format=data)

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON datetime object.

        :param datetime.datetime value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        # Check on empty.
        if not value:
            return None

        # Check format.
        output_format = getattr(self, 'format', DEFAULT_DATETIME_FORMAT)
        if output_format is None or isinstance(value, six.string_types):
            return value

        return value.strftime(output_format)


class JsonField(Field):
    """
    Field for custom JSON data.

    """
    default_error_messages = {
        'invalid': 'Value must be valid JSON.'
    }

    def to_internal_value(self, data):
        """
        Data transformation to python JSON object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: Union[dict, list]

        :raise ValidationError: If not valid data.

        """
        if isinstance(data, (dict, list)):
            return data

        try:
            return json.loads(data, encoding='utf8')
        except (JSONDecodeError, TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param Union[dict, list] value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        try:
            return json.dumps(value)
        except (TypeError, ValueError):
            self.fail('invalid')


class DictField(JsonField):
    """
    Field for custom DICT data.

    """
    child = _UnvalidatedField()
    default_error_messages = {
        'not_a_dict': 'Expected a dictionary of items but got type "{input_type}".'
    }

    def __init__(self, child=None, *args, **kwargs):
        """
        Field for custom DICT data.

        :param rest_framework.serializers.Field child: Field describing the type of dict elements.

        """
        super().__init__(*args, **kwargs)

        self.child = child or self.child

        # Check field `child`.
        if all((not isinstance(child, Field), not isinstance(self.child, Field))):
            raise ValueError('`child=` or `self.child` must be Field.')

        self.child.bind(field_name='', parent=self)  # Bind child field.

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            child=self.child
        )

    def to_internal_value(self, data):
        """
        Data transformation to python JSON object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: dict

        :raise ValidationError: If not valid data.

        """
        if html.is_html_input(data):
            data = html.parse_html_dict(data)

        if not isinstance(data, dict):
            self.fail('not_a_dict', input_type=type(data).__name__)

        return {
            six.text_type(key): self.child.run_validation(value)
            for key, value in six.iteritems(data)
        }

    def to_representation(self, value):
        """
        Transformation an object to a valid JSON object.

        :param dict value: The object to transformation.

        :return: Transformed data.
        :rtype: str

        """
        return {
            six.text_type(key): self.child.to_representation(val) if val is not None else None
            for key, val in six.iteritems(value)
        }


class SerializerMethodField(Field):
    """
    A field that get its representation from calling a method on the
    parent serializer class. The method called will be of the form
    "get_{field_name}" and "pop_{field_name}", and should take a single argument, which is the
    object being serialized.

    For example:

    class ExampleSerializer(self):
        extra_info = SerializerMethodField()

        def get_extra_info(self, obj):
            return ...  # Calculate some data to return.

        def pop_extra_info(self, data):
            return ...  # Serializing some data to return.

    """
    default_method_name_get_template = 'get_{field_name}'
    default_method_name_pop_template = 'pop_{field_name}'

    def __init__(self, method_name_get=None, method_name_pop=None,  *args, **kwargs):
        """
        A field that get its representation from calling a method on the
        parent serializer class. The method called will be of the form
        "get_{field_name}" and "pop_{field_name}", and should take a single argument, which is the
        object being serialized.

        :param str method_name_get: Method name for get data from python object.
        :param str method_name_pop: Method name for get data from request body.

        """
        kwargs['required'] = False
        super(SerializerMethodField, self).__init__(*args, **kwargs)

        self.method_name_get = method_name_get
        self.method_name_pop = method_name_pop

    def __deepcopy__(self, memo={}):
        return self.__class__(
            required=self.required, default=self.default, label=self.label,
            validators=self._src_validators, error_messages=self._src_messages,
            method_name_get=self.method_name_get, method_name_pop=self.method_name_pop
        )

    def bind(self, field_name, parent):
        """
        Initialization field name and parent instance .
        Called when a field is added to an instance of the parent.

        In order to enforce a consistent style, we error if a redundant
        'method_name_[get, pop]' argument has been used. For example:
        my_field = serializer.SerializerMethodField(method_name_get='get_my_field')

        :param str field_name: Field name.
        :param Serializer parent: Serializer class on which the field is located.

        """
        default_method_name_get = self.default_method_name_get_template.format(field_name=field_name)
        default_method_name_pop = self.default_method_name_pop_template.format(field_name=field_name)

        assert self.method_name_get != default_method_name_get, (
            "It is redundant to specify `%s` on SerializerMethodField '%s' in "
            "serializer '%s', because it is the same as the default method get name. "
            "Remove the `method_name_get` argument." %
            (self.method_name_get, field_name, parent.__class__.__name__)
        )
        assert self.method_name_pop != default_method_name_pop, (
                "It is redundant to specify `%s` on SerializerMethodField '%s' in "
                "serializer '%s', because it is the same as the default method pop name. "
                "Remove the `method_name_pop` argument." %
                (self.method_name_pop, field_name, parent.__class__.__name__)
        )

        # The method name should default to `get_{field_name}`.
        if self.method_name_get is None:
            self.method_name_get = default_method_name_get
        # The method name should default to `pop_{field_name}`.
        if self.method_name_pop is None:
            self.method_name_pop = default_method_name_pop

        super(SerializerMethodField, self).bind(field_name, parent)

    def _get_attribute(self, instance):
        """
        Searches for and returns an attribute on an object..

        :return: Object attribute value.
        :rtype: object

        :raise SkipError: If you could not find the field and the field is required.
        :raise Exception: If an error occurred during the search.

        """
        return self.to_internal_value(instance)

    def to_representation(self, value):
        """
        Transformation an object to a custom user object.

        :param object value: The object to transformation.

        :return: Transformed data.
        :rtype: object

        """
        method = getattr(self.parent, self.method_name_get)
        return method(value)

    def to_internal_value(self, data):
        """
        Data transformation to python custom user object.

        :param str data: Data for transformation.

        :return: Transformed data.
        :rtype: object

        :raise ValidationError: If not valid data.

        """
        method = getattr(self.parent, self.method_name_pop)
        return method(data)
