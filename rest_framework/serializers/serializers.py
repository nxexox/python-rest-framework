"""
Serializers.

"""
import copy
import inspect
try:
    from typing import Mapping
except ImportError:
    from collections import Mapping

from collections import OrderedDict

import six

from rest_framework.serializers.fields import Field, SerializerMethodField
from rest_framework.serializers.helpers import BindingDict
from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError
from rest_framework.utils import html


LIST_SERIALIZER_KWARGS = (
    'required', 'default', 'label', 'error_messages', 'allow_empty',
    'instance', 'data', 'min_length', 'max_length'
)  # The argument list for the ListSerializer to control the creation of many=True.


class MroFieldsSearch(object):
    """
    Class for search MRO fields on serializer.

    """
    def __init__(self, cls):
        self.cls = cls

    def get_fields(self, cls=None):
        """
        Search and return fields on order MRO.

        :param rest_framework.serializers.Serializer cls: Serializer class for search fields.

        :return: Dict fields for class on order MRO.
        :rtype: collections.OrderedDict

        """
        _declared_fields = OrderedDict()

        for _cls in reversed((cls or self.cls).__mro__):
            _current_fields = self.get_fields_from_cls(_cls)
            # print(_cls, _current_fields)
            _declared_fields.update(_current_fields)

        return _declared_fields

    def get_fields_from_cls(self, cls):
        """
        Search fields for one class.

        :param rest_framework.serializers.Serializer cls: Class for search fields.

        :return: Dict fields for class.
        :rtype: collections.OrderedDict

        """
        _declared_fields = OrderedDict()

        # Fill storage of fields.
        for name, obj in six.iteritems(cls.__dict__):
            if isinstance(obj, Field):
                _declared_fields[name] = obj

        # Forward storage of fields to the class itself.
        return _declared_fields


class BaseSerializerMeta(type):
    """
    Metaclass to create serializers.

    """
    def __new__(cls, name, bases, attrs):
        """
        Create a list of fields with the serializer.

        :param str name: The name of the class being created.
        :param tuple bases: Base class tuple.
        :param dict attrs: Attribute dict.

        """
        _cls = super().__new__(cls, name, bases, attrs)  # Create serializer class.

        # Get serializer fields.
        _declared_fields = MroFieldsSearch(_cls).get_fields()
        setattr(_cls, '_declared_fields', _declared_fields)  # Ser fields information on serializer.

        return _cls


class BaseSerializer(six.with_metaclass(BaseSerializerMeta, Field)):
    """
    Base class serializer.

    """
    def __init__(self, instance=None, data=None, *args, **kwargs):
        """
        Creating a serializer. The serializer should behave like a Field so that nesting can be done.

        :param object instance: Python object to transformation.
        :param dict data: The data that came in the request.

        """
        super().__init__(*args, **kwargs)
        self.instance = instance
        if isinstance(data, Mapping):
            self.initial_data = data

    def __new__(cls, *args, **kwargs):
        """
        Automatically create classes for `many = True`,

        """
        many = kwargs.pop('many', False)
        if bool(many):
            return cls.many_init(*args, **kwargs)
        return super(BaseSerializer, cls).__new__(cls)

    def __deepcopy__(self, memo={}):
        return self.__class__(instance=self.instance, data=self.data)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method implements the creation of the parent class `ListSerializer`,
        when `many = True` is used. You can customize it if you need to determine
        which keyword arguments are passed to the parent element,
        and which are passed to the child.

        """
        child_serializer = cls(*args, **kwargs)  # Make child serializer.

        # Passing arguments to the ListSerializer.
        list_kwargs = {'child': child_serializer}
        list_kwargs.update({
            key: value for key, value in six.iteritems(kwargs)
            if key in LIST_SERIALIZER_KWARGS
        })

        # Creating ListSerializer.
        return ListSerializer(*args, **list_kwargs)

    def validate(self, data):
        """
        Manual validation of serializer full data.

        :param dict data: Transformed and validated data for manual validation.

        :return: Validated data. Be careful, be sure to return.
        :rtype: dict

        """
        return data

    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param dict data: Data for transformation.

        :return: Transformed data.
        :rtype: dict

        """
        raise NotImplementedError('`.to_internal_value()` must be implemented.')

    def to_representation(self, instance):
        """
        Transformation an object to a valid JSON object.

        :param object instance: The object to transformation.

        :return: Transformed data.
        :rtype: dict

        """
        raise NotImplementedError('`.to_representation()` must be implemented.')

    def is_valid(self, raise_exception=False):
        """
        Validates the data that came into the serializer.

        :param bool raise_exception: Is there an exception if validation fails?

        :return: Validation result.
        :rtype: bool

        """
        raise NotImplementedError('`.is_valid()` must be implemented.')

    @property
    def validated_data(self):
        """
        Validated data.

        :return: Validated data.
        :rtype: dict

        """
        raise NotImplementedError('`.validated_data` must be implemented.')

    @property
    def errors(self):
        """
        Errors during validation.

        :return: Errors during validation.
        :rtype: dict

        """
        raise NotImplementedError('`.errors` must be implemented.')

    @property
    def fields(self):
        """
        Serializer fields. Create _fields attribute BindingDict type.
        Call bind method on all fields.
        Return deep copy dict.

        :return: Dict serializer fields.
        :rtype: rest_framework.serializers.helpers.BindingDict

        """
        if not hasattr(self, '_fields'):
            self._fields = BindingDict(self)
            # TODO: FIXME Architecture. many call bind methods. On create serializer object
            # Call bind method. In metaclass not access to create class.
            for field_name, field_obj in six.iteritems(self.get_fields()):
                self._fields[field_name] = field_obj

        return self._fields

    def get_fields(self):
        """
        Returns a dictionary of {field_name: field_instance}.
        Every new serializer is created with a clone of the field instances.
        This allows users to dynamically modify the fields on a serializer
        instance without affecting every other serializer instance.

        :return: Deep copy declare fields.
        :rtype: dict

        """
        
        return copy.deepcopy(self._declared_fields)

    @property
    def data(self):
        """
        Serialized object.

        :return: Serialized object.
        :rtype: dict

        """
        if hasattr(self, 'initial_data') and not hasattr(self, '_validated_data'):
            msg = (
                'When a serializer is passed a `data` keyword argument you '
                'must call `.is_valid()` before attempting to access the '
                'serialized `.data` representation.\n'
                'You should either call `.is_valid()` first, '
                'or access `.initial_data` instead.'
            )
            raise AssertionError(msg)

        if not hasattr(self, '_data'):
            if self.instance is not None and not getattr(self, '_errors', None):
                self._data = self.to_representation(self.instance)
            elif hasattr(self, '_validated_data') and not getattr(self, '_errors', None):
                self._data = self.to_representation(self._validated_data)
            else:
                self._data = self.get_default()
        return self._data


class Serializer(BaseSerializer):
    """
    Serializer class.

    """
    def to_internal_value(self, data):
        """
        Data transformation to python object.

        :param dict data: Data for transformation.

        :return: Transformed data.
        :rtype: dict

        :raise ValidationError: If not valid data.

        """
        return self._field_validation(self.fields, data)

    def to_representation(self, instance):
        """
        Transformation an object to a valid JSON object.

        :param object instance: The object to transformation.

        :return: Transformed data.
        :rtype: object

        """
        res = OrderedDict()  # Attributes storage.

        for field_name, field_val in six.iteritems(self.fields):
            # TODO: mini hack
            if not isinstance(field_val, SerializerMethodField):
                # We try to get the attribute.
                try:
                    attribute = field_val.get_attribute(instance)
                except SkipError:
                    # TODO: That thing, throw an error, if the attribute of the object is not found, or skip?
                    continue
            else:
                attribute = instance

            # We try to turn it into a JSON valid format.
            res[field_name] = field_val.to_representation(attribute)

        # Return.
        return res

    def _manual_validate_method(self, field_name, validated_value):
        """
        Manual validation of a specific field.

        :param str field_name: Field name.
        :param object validated_value: Field value.

        :return: Validation value.
        :rtype: object

        """
        # We look, if there is a method of manual validation, we call it..
        manual_validate_method = getattr(self, 'validate_' + field_name, None)
        if callable(manual_validate_method):
            validated_value = manual_validate_method(validated_value)
        return validated_value

    def _field_validation(self, fields_dict, data):
        """
        Validation add fields

        :param dict fields_dict: Dictionary with initialized fields that we validate.
        :param dict data: Data that is validated.

        :return: Validated and transformed data.
        :raise ValidationError: If errors occurred during validation.

        """
        validated_data, errors = OrderedDict(), OrderedDict()
        # Running through the fields.
        for field_name, field_obj in six.iteritems(fields_dict):
            try:
                # Transform to python type and validate each field.
                validated_val = field_obj.run_validation(data.get(field_name, None))

                # Now manual validation.
                validated_val = self._manual_validate_method(field_name, validated_val)

                # And if there was a field in the incoming data, then we save it in the converted form.
                if field_name in data or field_obj.default:
                    validated_data[field_name] = validated_val or field_obj.default

            except ValidationError as e:
                # If not passed validation, save the error.
                errors[field_name] = e.detail

        if any(errors):
            raise ValidationError(errors)

        return validated_data

    def is_valid(self, raise_exception=False):
        """
        Validates the data that came into the serializer.

        :param bool raise_exception: Whether to throw an exception if validation failed?

        :return: Validation result.
        :rtype: bool

        """
        if not hasattr(self, 'initial_data'):
            raise AssertionError(
                'Cannot call `.is_valid()` as no `data=` keyword argument '
                'was passed when instantiating the serializer instance.'
            )

        # Preparing storage for results.
        self._errors, self._validated_data = OrderedDict(), OrderedDict()

        # Validated all fields.
        try:
            self._validated_data = self._field_validation(self.fields, self.initial_data)
        except ValidationError as e:
            self._errors = e.detail

        # Now run the full manual validation method.
        try:
            self._validated_data = self.validate(self._validated_data) if not self._errors else self._validated_data
        except ValidationError as e:
            self._errors['errors'] = e.detail

        # If you need to throw an error, we throw.
        if self._errors and raise_exception:
            self._validated_data = OrderedDict()
            raise ValidationError(self._errors)

        # Return validation result.
        return not bool(self._errors)

    def run_validation(self, data):
        """
        Runs validation on the current serializer..

        :param object data: Data for validation.

        :return: Transformed and validated data.
        :rtype: dict

        """
        # We first check to see if an empty field has arrived?
        is_empty, data = self.validate_empty_values(data)

        # Transformed to python type.
        value = self.to_internal_value(data)

        # Validating validators.
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '`.validate ()` should return a valid value.'

        except ValidationError as e:
            raise ValidationError(detail=e.detail)

        # We return the validated and transformed value.
        return value

    @property
    def validated_data(self):
        """
        Validated data.

        :return: Validated data.
        :rtype: dict

        """
        if not hasattr(self, '_validated_data'):
            raise AssertionError('You must call `.is_valid()` before accessing `.validated_data`.')
        return self._validated_data.copy()

    @property
    def errors(self):
        """
        Errors during validation.

        :return: Errors during validation.
        :rtype: dict

        """
        if not hasattr(self, '_errors'):
            raise AssertionError('You must call `.is_valid()` before accessing `.errors`.')
        return self._errors.copy()


class ListSerializer(Serializer):
    """
    Serializer for the list of objects.

    """
    child = None  # Child serializer.

    default_error_messages = {
        'not_a_list': 'Expected a list of items but got type "{input_type}".',
        'empty': 'This list may not be empty.',
    }

    def __init__(self, child=None, allow_empty=None, *args, **kwargs):
        """
        Serializer for the list of objects.

        :param rest_framework.serializers.Field child: Child serializer.
        :param bool allow_empty: Allow empty list?

        """
        self.child = child or copy.deepcopy(self.child)
        self.allow_empty = bool(allow_empty)

        # We check that the data is correct.
        assert self.child is not None, '`child` is a required argument'
        assert not inspect.isclass(self.child), '`child` has not been instantiated.'

        # Initializing serializer.
        super(ListSerializer, self).__init__(*args, **kwargs)
        # Bind child serializer.
        self.child.bind(field_name='', parent=self)

    def __deepcopy__(self, memo={}):
        return self.__class__(
            instance=self.instance, data=self.data,
            child=self.child, allow_empty=self.allow_empty
        )

    def to_internal_value(self, data):
        """
        Data transformation to python list object.

        :param object data: Data for transformation.

        :return: Transformed data.
        :rtype: list

        :raise ValidationError: If data not valid.

        """
        # Parse data.
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        # Initial validation that came in an array.
        if not isinstance(data, list):
            message = self.error_messages['not_a_list'].format(
                input_type=type(data).__name__
            )
            raise ValidationError({'non_field_errors': [message]}, code='not_a_list')

        # Validation that this is not an empty value and whether it is empty.
        if not self.allow_empty and len(data) == 0:
            message = self.error_messages['empty']
            raise ValidationError({'non_field_errors': [message]}, code='empty')

        res, errors = [], []  # Make storage for results.

        # Validating each item from the list.
        for item in data:
            try:
                value = self.child.run_validation(item)
            except ValidationError as e:
                res.append({})
                errors.append(e.detail)
            else:
                res.append(value)
                errors.append({})

        # If the conversion and validation failed.
        if any(errors):
            raise ValidationError(errors)

        # We return the transformed and validated data.
        return res

    def to_representation(self, instance):
        """
        Transformation an object to a valid JSON list object.

        :param list instance: The object to transformation.

        :return: Transformed data.
        :rtype: list

        """
        return [self.child.to_representation(item) for item in instance]

    def is_valid(self, raise_exception=False):
        """
        Validates the data that came into the serializer.

        :param bool raise_exception: Is there an exception if validation fails?

        :return: Validation result.
        :rtype: bool

        """
        if not hasattr(self, 'initial_data'):
            raise AssertionError(
                'Cannot call `.is_valid()` as no `data=` keyword argument '
                'was passed when instantiating the serializer instance.'
            )

        # Preparing storage for results.
        self._errors, self._validated_data = [], []

        # Validating all fields
        try:
            self._validated_data = self.to_internal_value(self.initial_data)
        except ValidationError as e:
            self._errors = e.detail

        # If you need to throw an error, we throw.
        if self._errors and raise_exception:
            self._validated_data = []
            raise ValidationError(self._errors)

        # Return validation result.
        return not bool(self._errors)

    @property
    def validated_data(self):
        """
        Validated data.

        :return: Validated data.
        :rtype: list

        """
        if not hasattr(self, '_validated_data'):
            raise AssertionError('You must call `.is_valid()` before accessing `.validated_data`.')
        return self._validated_data[:]

    @property
    def errors(self):
        """
        Errors during validation.

        :return: Errors during validation.
        :rtype: list

        """
        if not hasattr(self, '_errors'):
            raise AssertionError('You must call `.is_valid()` before accessing `.errors`.')
        return self._errors[:]
