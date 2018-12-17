"""
Testing serializers.
1. Test methods and call logic separately.
2. We test the external interface as they should work.

"""
# import collections
try:
    from typing import Mapping
except ImportError:
    from collections import Mapping
from unittest import TestCase

import six

from rest_framework.serializers.fields import (
    CharField, BooleanField, IntegerField, FloatField, ListField
)
from rest_framework.serializers.serializers import BaseSerializer, Serializer, ListSerializer
from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError

from rest_framework.tests.serializers_for_tests import (
    SerializerPrimitiveField, SerializerMixinSingle, SerializerMixinMany, SerializerMixinRequired,
    InheritSecondLevelChild
)


class BaseSerializerTestClass(TestCase):
    """
    Class for testing logic and serializer methods.

    """
    serializer_class = BaseSerializer
    abstract_methods = {
        'to_internal_value': {'data': None},
        'to_representation': {'instance': None},
        'is_valid': {},
        'validated_data': {},
        'errors': {}
    }
    validate_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    to_internal_value_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    to_representation_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    is_valid_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    validated_data_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    errors = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )

    # Class for testing on empty.
    class Empty:
        pass

    def create_params(self, **params):
        """
        Create params, for create serializer.

        :return: Params for create serializers.
        :rtype: dict

        """
        return params

    def __test_method_cases(self, method_name):
        """
        Testing methods on cases.

        :param str method_name: Method name for cases testing.

        """
        # Check all cases.
        for case in getattr(self, '%s_cases' % method_name, []):
            # Skip case.
            if not case:
                continue

            try:
                # Get the data.
                data, result = case.get('data', {}), case.get('return', None)
                params, exceptions = case.get('params', {}), case.get('exceptions', {})
                create_ser = case.get('create_ser', None)

                data = data or {}  # Transform None into dict.

                # Building a serializer and looking for a method to test..
                if callable(create_ser):
                    serializer = create_ser(**self.create_params(**params))
                else:
                    serializer = self.serializer_class(**self.create_params(**params))

                method = getattr(serializer, method_name, self.Empty())
                if isinstance(method, self.Empty):
                    self.fail('Testing on cases failed. Method not found `{}` have class `{}`.'.format(
                        method_name, serializer.__class__.__name__
                    ))

                # If errors are expected.
                if exceptions:
                    try:
                        res = method(**data) if callable(method) else method
                        self.fail('In method `{}.{}()` case `{}` not raise error. Method return: `{}`.'.format(
                            serializer.__class__.__name__, method_name, case, res
                        ))
                    except tuple(exceptions):
                        pass
                else:
                    # If no errors are expected.
                    res = method(**data) if callable(method) else method
                    assert res == result, \
                        'In method `{}.{}()` case {} return incorrect result `{}`'.format(
                            serializer.__class__.__name__, method_name, case, res
                        )
            except Exception as e:
                self.fail('During the inspection of the case  `{}` for method `{}.{}` an unexpected error occurred: `{}: {}`'.format(
                    case, self.serializer_class.__class__.__name__, method_name, e.__class__.__name__, e
                ))

    def test_init(self):
        """
        Testing create.

        """
        # Create with as empty data.
        ser = self.serializer_class()
        assert ser.instance is None, '`.instance` must be None. Reality `{}`.'.format(ser.instance)
        assert getattr(ser, 'initial_data', None) is None, '`.initial_data` must be None. Reality `{}`.'.format(
            getattr(ser, 'initial_data', None)
        )

        # Create with as empty object.
        obj = type('object', (object,), {})
        ser = self.serializer_class(obj)
        assert ser.instance == obj, '`.instance` must be {}. Reality `{}`.'.format(obj, ser.instance)
        assert getattr(ser, 'initial_data', None) is None, '`.initial_data` must be None. Reality `{}`.'.format(
            getattr(ser, 'initial_data', None)
        )

        # Create with data.
        obj = {}
        ser = self.serializer_class(data=obj)
        assert ser.instance is None, '`.instance` must be None. Reality `{}`.'.format(ser.instance)
        assert getattr(ser, 'initial_data', None) == obj, '`.initial_data` must be {}. Reality `{}`.'.format(
            obj, getattr(ser, 'initial_data', None)
        )

    def test_validate_cases(self):
        """
        We test data forwarding.

        """
        self.__test_method_cases('validate')

    def test_abstract_methods(self):
        """
        Testing abstract merhods.

        """
        field = self.serializer_class(**self.create_params())
        for method_name, method_params in six.iteritems(self.abstract_methods):
            try:
                # Works for both methods and abstract properties.
                getattr(field, method_name, lambda: None)(**method_params)
                self.fail('Method `.{}` must throw as exception `NotImplementedError`.'.format(method_name))
            except NotImplementedError:
                pass

    def test_to_internal_value_cases(self):
        """
        A test for converting data to a valid python object.

        """
        if 'to_internal_value' not in self.abstract_methods:
            self.__test_method_cases('to_internal_value')

    def test_to_representation_cases(self):
        """
        Test data conversion to a valid JSON object.

        """
        if 'to_representation' not in self.abstract_methods:
            self.__test_method_cases('to_representation')

    def test_is_valid_cases(self):
        """
        Testing validation and data processing.

        """
        if 'is_valid' in self.abstract_methods:
            self.__test_method_cases('is_valid')

    def test_validated_data_cases(self):
        """
        Testing validated_date property.

        """
        if 'validated_data' not in self.abstract_methods:
            self.__test_method_cases('validated_data')

    def test_errors(self):
        """
        Test errors property.

        """
        if 'errors' not in self.abstract_methods:
            self.__test_method_cases('errors')

    def test_fields(self):
        """
        Testing the properties of fields.

        """
        pass

    def test_data(self):
        """
        Testing properties with validated converted data.

        """
        pass


# TODO: Finish cases
class SerializerTestClass(TestCase):
    """
    Testing class serializer methods.

    """
    serializer_class = Serializer
    abstract_methods = {}
    validate_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': None}, 'return': None},
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': 'qwe'}, 'return': 'qwe'}
    )
    to_internal_value_cases = (
        {},
    )
    to_representation_cases = (
        {},
    )
    is_valid_cases = (
        {},
    )
    validated_data_cases = (
        {},
    )
    errors = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # create_ser - is a function that accepts params as input and a serializer that is ready for testing.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )

    def create_serializer(self):
        """
        The function of creating a serializer for subsequent testing of methods.

        """
        pass


class SerializerUserTestCase(TestCase):
    """
    Testing serializer for use.
    When we write tests, it is enough to inherit from the class,
    Define the attribute serializer_class,
    Implement methods: create_params.

    """
    serializer_class = SerializerPrimitiveField
    fullness_types = ('empty', 'middle', 'full', 'validation_error')
    # TODO: To think what to do with default values.

    def __create_object(self, data):
        """
        Recursive creation of an object from a dictionary.

        :param dict data: Data that is being converted to in object attributes.

        :return: Created object.
        :rtype: object

        """
        return type('object', (object,), {
            key: self.__create_object(val) if isinstance(val, Mapping) else val
            for key, val in six.iteritems(data)
        })

    def __create_params(self, fullness=None):
        """
        Create data for serializer. Internal method, the layer before the user.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`,` validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness not in self.fullness_types:
            self.fail('The type of data to be generated must be one of `{}`, reality `{}`.'.format(
                self.fullness_types, fullness
            ))
        return self.create_params(fullness)

    def create_params(self, fullness):
        """
        Create data for serializer.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`,` validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True}
        elif fullness == 'validation_error':
            return {}
        else:
            return {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}

    def test_data_serializer(self):
        """
        Testing the data attribute for a serializer.

        """
        # First we feed him empty data.
        ser = self.serializer_class(data=self.__create_params(fullness='empty'))
        assert ser.is_valid() is False, '`.is_valid()` must return False.'
        assert isinstance(ser.errors, Mapping), \
            '`.errors` must be dict. Reality: {}.'.format(type(ser.errors))
        assert len(ser.errors) > 0, '`.errors` must contain errors.'
        assert isinstance(ser.validated_data, Mapping), \
            '`.validated_data` must be dict. Reality: {}.'.format(type(ser.validated_data))
        assert len(ser.validated_data) == 0, '`.validated_data` must be empty. Reality: {},'.format(ser.validated_data)

        # We check that the exception is thrown in case of errors.
        ser = self.serializer_class(data=self.__create_params(fullness='validation_error'))
        try:
            ser.is_valid(raise_exception=True)
            self.fail('`.is_valid(raise_exception=True)` must throw as exception `ValidationError`.')
        except ValidationError:
            pass

        # Now we feed the data partially.
        ser = self.serializer_class(data=self.__create_params(fullness='middle'))
        assert ser.is_valid() is False, '`.is_valid()` must return False.'
        assert isinstance(ser.errors, Mapping), \
            '`.errors` must be dict. Reality: {}.'.format(type(ser.errors))
        assert len(ser.errors) > 0, '`.errors` must contain errors.'
        assert isinstance(ser.validated_data, Mapping), \
            '`.validated_data` must be dict. Reality: {}.'.format(type(ser.validated_data))
        assert len(ser.validated_data) == 0, '`.validated_data` must be empty. Reality: {}.'.format(ser.validated_data)

        # Now we feed the data completely.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(data=data)
        # Check logic.
        assert ser.is_valid() is True, '`.is_valid()` must return True.'
        assert isinstance(ser.errors, Mapping), \
            '`.errors` must be dict. Reality: {}.'.format(type(ser.errors))
        assert len(ser.errors) == 0, '`.errors` must be empty. Reality: {}.'.format(ser.errors)
        assert isinstance(ser.validated_data, Mapping), \
            '`.validated_data` must be dict. Reality: {}.'.format(ser.validated_data)
        assert len(ser.validated_data) > 0, '`.validated_data` must contain data.'
        # We check that all data is returned correctly.
        for k, v in six.iteritems(ser.validated_data):
            if k in data:
                assert v == data[k]
                del data[k]
        assert len(data) == 0, 'All data in `.validated_data` must match the data in` data=`.'

    def test_instance_object_serializer(self):
        """
        Testing the instance attribute for the serializer.
        Feed the object.

        """
        # First we feed him an empty object.
        ser = self.serializer_class(instance=self.__create_object(self.__create_params(fullness='empty')))
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}'.format(type(ser.data))

        # Now we feed the data partially.
        data = self.__create_params(fullness='middle')
        ser = self.serializer_class(instance=self.__create_object(data))
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}.'.format(type(ser.data))
        for k, v in six.iteritems(ser.data):
            if k in data:
                assert v == data[k], 'Object attribute `{}` must be `{}`, reality `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'The size of the data must match the original. Left: {}.'.format(data)

        # Now we feed the data completely.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(instance=self.__create_object(data))
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}.'.format(type(ser.data))
        for k, v in six.iteritems(ser.data):
            if k in data:
                assert v == data[k], 'Object attribute `{}` must be `{}`, reality `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'The size of the data must match the original. Left: {}.'.format(data)

    def test_instance_dict_serializer(self):
        """
        Testing the instance attribute for a serializer with primitives.
        Feed the dictionary.

        """
        # First we feed him an empty object..
        ser = self.serializer_class(instance=self.__create_params(fullness='empty'))
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}.'.format(type(ser.data))

        # Now we feed the data partially.
        data = self.__create_params(fullness='middle')
        ser = self.serializer_class(instance=data)
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}.'.format(type(ser.data))
        for k, v in six.iteritems(ser.data):
            if k in data:
                assert v == data[k], 'Object attribute`{}` must be `{}`, reality `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'The size of the data must match the original. Left: {}.'.format(data)

        # Now we feed the data completely.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(instance=data)
        assert isinstance(ser.data, Mapping), '`.data` must be dict. Reality: {}.'.format(type(ser.data))
        for k, v in six.iteritems(ser.data):
            if k in data:
                assert v == data[k], 'Object attribute `{}` must be `{}`, reality `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'The size of the data must match the original. Left: {}.'.format(data)


class SerializerSingleMixinTestCase(SerializerUserTestCase):
    """
    Testing a serializer with a single object embedded serializer.

    """
    serializer_class = SerializerMixinSingle

    def create_params(self, fullness):
        """
        Create data for serializer.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`, `validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': {'integer_f': 123, 'bool_f': True}}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}
            }


class SerializerManyMixinTestCase(SerializerUserTestCase):
    """
    Testing a serializer with an embedded serializer with multiple objects.

    """
    serializer_class = SerializerMixinMany

    def create_params(self, fullness):
        """
        Create data for serializer.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`, `validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': [{'integer_f': 123, 'bool_f': True}]}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': [{'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}]
            }


class SerializerRequiredMixinTestCase(SerializerUserTestCase):
    """
    Testing the serializer with the obligatory serializer attached.

    """
    serializer_class = SerializerMixinRequired

    def create_params(self, fullness):
        """
        Create data for serializer.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`, `validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': {'integer_f': 123, 'bool_f': True}}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}
            }


class SerializerInheritTestCase(SerializerUserTestCase):
    """
    Testing the serializer with many levels inherit.

    """
    serializer_class = InheritSecondLevelChild

    def create_params(self, fullness):
        """
        Create data for serializer.

        :param str fullness: Type of data creation: `empty`,` middle`, `full`, `validation_error`.

        :return: Data dict.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'root': 100, 'first_level_child': 50}
        elif fullness == 'validation_error':
            return {}
        else:
            return {'root': 100, 'first_level_child': 50, 'second_level_child': 100}
