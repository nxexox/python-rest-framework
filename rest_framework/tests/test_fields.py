"""
Fields testing

"""
import datetime
from unittest import TestCase

import six

from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError
from rest_framework.serializers.fields import (
    Field, CharField, IntegerField, FloatField, BooleanField, ListField,
    TimeField, DateField, DateTimeField,
    JsonField, DictField,
    SerializerMethodField,
    get_attribute
)
from rest_framework.serializers.validators import (
    RequiredValidator, MaxValueValidator, MinValueValidator, MinLengthValidator, MaxLengthValidator
)

from rest_framework.tests.serializers_for_tests import SerializerMethodFieldDefault, SerializerMethodFieldSingle


class BaseFieldTestCase(TestCase):
    """
    Testing base field class.

    """
    field_class = Field
    abstract_methods = {
        'to_internal_value': {'data': None},
        'to_representation': {'value': None},
    }  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.

    to_representation_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        # data - arguments, return - return, params - arguments __init__, exceptions - expected errors
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Cases, to test the performance of `.run_validation()`.

    field_error_messages = {}  # Custom field error key list.

    _fields_vals = {
        'required': True, 'default': None, 'label': None, 'validators': [],
        'error_messages': {}, 'default_error_messages': {}, 'default_validators': []
    }
    __error_messages = {'required': None, 'null': None}  # Default list of errors.

    # Class for testing for empty.
    class Empty:
        pass

    @classmethod
    def setUpClass(cls):
        """
        We supplement the data for each field separately.

        """
        cls.__error_messages.update(cls.field_error_messages)

    def assert_base_fields(self, field, **additional_fields):
        """
        Checks on all base fields and extras.

        :param rest_framework.serializers.fields.Field field: Field object.
        :param additional_fields: Dict additional attributes to check.

        """
        copy_fields = self._fields_vals.copy()
        copy_fields.update(additional_fields)
        msg = 'Invalid value in %s for field: {}. Expected: {}, Reality: {}.' % field.__class__.__name__

        for key, val in six.iteritems(copy_fields):
            field_val = getattr(field, key, self.Empty())
            # We try to check in three ways, depending on the type.
            if isinstance(val, (bool, type(None))):  # First single types.
                assert val is field_val, msg.format(key, val, field_val)
            elif isinstance(val, (six.string_types + six.integer_types + (float,))):  # Now primitives.
                assert val == field_val, msg.format(key, val, field_val)
            else:  # If the object is complex.
                assert isinstance(val, type(field_val)), msg.format(key, val, type(field_val))

    def create_params(self, **params):
        """
        Creating parameters to create a field object.

        :return: Parameters for creating a field.
        :rtype: dict

        """
        r_params = self.requirement_arguments_for_field.copy()
        r_params.update(params)
        return r_params

    def assert_bind(self, field, field_name=None, parent=None, label=None):
        """
        Checks the effects of the bind method.

        :param rest_framework.serializers.fields.Field field: Object for check.
        :param str field_name: Field name.
        :param object parent: Parent field.
        :param str label: Label field.

        """
        assert field.label == label, '`.label` expected {}, reality {}.'.format(label, field.label)
        assert field.parent == parent, '`.parent` expected {},  reality {}.'.format(parent, field.parent)
        assert field.field_name == field_name, \
            '`.field_name` expected {}, reality {}.'.format(field_name, field.field_name)

    def create_method_for_get_attribute(self, field_name=None, call_bind=True,
                                        default=None, required=None, attr=None, set_self=True, **kwargs):
        """
        Creating an attribute on an object to test `field.get_attribute ()`

        :param str field_name: Field name.
        :param bool call_bind: Do I need to call the bind method in a field?
        :param object default: Default value.
        :param bool required: Is required field?
        :param object attr: The attribute itself that we put.
        :param bool set_self: Do I need to set the link to the class parent?.

        :return: Created and ready for testing Field.
        :rtype: rest_framework.serializers.fields.Field

        """
        field = self.field_class(**self.create_params(required=required, default=default, **kwargs))
        if call_bind:
            field.bind(field_name, self)
        if set_self:
            setattr(self, field_name, attr)
        return field

    def __test_method_cases(self, method_name):
        """
        Testing methods by cases.

        :param str method_name: Method name for testing by cases.

        """
        # Check all cases
        for case in getattr(self, '%s_cases' % method_name, []):
            # Skip case.
            if not case:
                continue

            try:
                # Get the data.
                data, result = case.get('data', {}), case.get('return', None)
                params, exceptions = case.get('params', {}), case.get('exceptions', {})

                data = data or {}  # Transform None into dict.

                # Building a field and looking for a method to test..
                field = self.field_class(**self.create_params(**params))
                method = getattr(field, method_name, self.Empty())
                if isinstance(method, self.Empty):
                    self.fail('Testing by cases failed. Method not found `{}` have class `{}`.'.format(
                        method_name, field.__class__.__name__
                    ))

                # If errors are expected.
                if exceptions:
                    try:
                        res = method(**data)
                        self.fail('In method `{}.{}()` case `{}` not raise error. Method return: `{}`.'.format(
                            field.__class__.__name__, method_name, case, res
                        ))
                    except tuple(exceptions):
                        pass
                else:
                    # If no errors are expected.
                    res = method(**data)
                    assert res == result, \
                        'In method `{}.{}()` case {} return incorrect result `{}`'.format(
                            field.__class__.__name__, method_name, case, res
                        )
            except Exception as e:
                self.fail('During the inspection of the case `{}` for method `{}.{}` an unexpected error occurred: `{}: {}`'.format(
                    case, self.field_class.__class__.__name__, method_name, e.__class__.__name__, e
                ))

    def test_default_create(self):
        """
        Testing creation with default settings.

        """
        self.assert_base_fields(self.field_class(**self.create_params()))  # First make default.

        # Now create with settings.
        params = self.create_params(required=False)
        self.assert_base_fields(self.field_class(**params), **params)

        # See how default affects required..
        params = self.create_params(default='')
        self.assert_base_fields(self.field_class(**params), required=False, **params)

        # See how required affects validators..
        field = self.field_class(**self.create_params(required=True))
        assert isinstance(field.validators, list), \
            '`.validators` must be list, reality {}'.format(type(field.validators))
        assert len(field.validators) == 1, \
            'In `.validators` must be 1 validator, reality {}'.format(len(field.validators))
        assert isinstance(field.validators[0], RequiredValidator), \
            'In `.validators` must be `RequiredValidator`. Reality: `{}`'.format(type(field.validators[0]))
        # Now we check that there is no validator.
        field = self.field_class(**self.create_params(required=False))
        assert isinstance(field.validators, list), \
            '`.validators` must be list, reality {}'.format(type(field.validators))
        assert len(field.validators) == 0, \
            'In `.validators` there should be no validators, reality `{}`'.format(len(field.validators))

        # Check for error messages.
        field, messages_keys = self.field_class(**self.create_params()), self.__error_messages
        for key in field.error_messages:
            assert key in messages_keys, 'In `.error_messages` must be key `{}`.'.format(key)

        # We update the dictionary of errors, and we try with a custom error.
        new_error_message = self.__error_messages.copy()
        new_error_message['test'] = None
        field = self.field_class(**self.create_params(error_messages={'test': 'test'}))
        messages_keys = new_error_message

        for key in field.error_messages:
            assert key in messages_keys, 'In `.error_messages` must be key `{}`.'.format(key)

    def test_bind(self):
        """
        Testing bind method.

        """
        # First default.
        field = self.field_class(**self.create_params())
        field.bind('test_label', self)
        self.assert_bind(field, 'test_label', self, 'Test label')

        # Now change label.
        field = self.field_class(**self.create_params(label='test_label'))
        field.bind('test_label', self)
        self.assert_bind(field, 'test_label', self, 'test_label')

    def test_fail(self):
        """
        Testing fail method.

        """
        # We test without our errors.
        field = self.field_class(**self.create_params())
        try:
            field.fail('required')
            self.fail('`.fail()` must throw as exception `ValidationError`.')
        except ValidationError:
            pass
        try:
            field.fail('test')
            self.fail('`.fail()` must throw as exception `AssertionError`.')
        except AssertionError:
            pass

        # Now add custom error message
        field = self.field_class(**self.create_params(error_messages={'test': '{test}-test'}))
        try:
            field.fail('test', test='test')
            self.fail('`.fail()` must throw as exception `ValidationError`.')
        except ValidationError as e:
            assert e.detail == 'test-test', 'The error message should be `{}`, reality `{}`.'.format(
                'test-test', e.detail
            )

    def test_abstract_methods(self):
        """
        Testing abstract methods.

        """
        field = self.field_class(**self.create_params())
        for method_name, method_params in six.iteritems(self.abstract_methods):
            try:
                getattr(field, method_name, lambda: None)(**method_params)
                self.fail('Method `.{}` must throw as exception `NotImplementedError`.'.format(method_name))
            except NotImplementedError:
                pass

    def test_to_internal_value(self):
        """
        A test for converting data to a valid python object.

        """
        if 'to_internal_value' not in self.abstract_methods:
            self.__test_method_cases('to_internal_value')

    def test_to_representation(self):
        """
        Test data conversion to a valid JSON object.

        """
        if 'to_representation' not in self.abstract_methods:
            self.__test_method_cases('to_representation')

    def test_get_default(self):
        """
        Testing the get_default method.

        """
        field = self.field_class(**self.create_params())
        res = field.get_default()
        assert res is None, '`.get_default()` must return None, reality: {}.'.format(res)

        field = self.field_class(**self.create_params(default=1))
        res = field.get_default()
        assert res == 1, '`.get_default()` must return 1, reality: {}.'.format(res)

        field = self.field_class(**self.create_params(default=lambda: 100))
        res = field.get_default()
        assert res == 100, '`.get_default()` must return 100, reality: {}.'.format(res)

    def test_get_attribute(self):
        """
        Testing get_attribute method.

        """
        params = dict(
            field_name='test_get_attribute_field', call_bind=True, required=False, default=None,
            attr=self.test_get_attribute, set_self=True
        )

        # First normal work.
        res = self.create_method_for_get_attribute(**params).get_attribute(self)
        assert res == self.test_get_attribute, \
            '`.get_attribute()` must return {}, reality {}.'.format(self.test_get_attribute, res)

        # Now we try non-existent to look for and return default.
        params.update(default=100, call_bind=False, attr=None, set_self=False)
        res = self.create_method_for_get_attribute(**params).get_attribute(self)
        assert res == 100, '`.get_attribute()` must return 100, reality {}.'.format(res)

        # We see that if the field is mandatory and there is no default, it throws the exception `SkipError`.
        params.update(required=True, default=None)
        try:
            self.create_method_for_get_attribute(**params).get_attribute(self)
            self.fail('`.get_attribute()` must throw as exception `SkipError`.')
        except SkipError:
            pass

        # Now we try to get the original exception.
        params.update(field_name=None, required=False, call_bind=True)
        try:
            res = self.create_method_for_get_attribute(label='test', **params).get_attribute(self)
            self.fail('`.get_attribute()` must throw as exception `TypeError`, return `{}`.'.format(res))
        except TypeError:
            pass
        except Exception as e:
            self.fail('`.get_attribute()` must throw as exception `TypeError`, reality {}.'.format(type(e)))

    def test_validate_empty_values(self):
        """
        Testing validation on an empty type.

        """
        # First default settings.
        field = self.field_class(**self.create_params(required=False))
        is_empty, data = field.validate_empty_values(None)
        assert is_empty is True, '`.validate_empty_values()` must return True.'
        assert data is None, '`.validate_empty_values()` must return None.'

        # Now we check the response to the binding.
        field = self.field_class(**self.create_params(required=True))
        try:
            field.validate_empty_values(None)
            self.fail('`.validate_empty_values()` must throw as exception `ValidationError`.')
        except ValidationError:
            pass

        # Now we check for normal data
        field = self.field_class(**self.create_params(required=True))
        is_empty, data = field.validate_empty_values(123)
        assert is_empty is False, '`.validate_empty_values()` must return False.'
        assert data == 123, '`.validate_empty_values()` must return 123.'

    def test_run_validation(self):
        """
        Testing run_validation method

        """
        self.__test_method_cases('run_validation')

    def test_run_validation_base_field(self):
        """
        Testing start validation for base field.

        """
        to_internal_value = lambda x: x  # We do a mock for internal function.
        # Check on default settings.
        field = self.field_class(**self.create_params())
        setattr(field, 'to_internal_value', to_internal_value)
        res = field.run_validation(123)
        assert res == 123, '`.run_validation()` must return 123.'

        # Check when the field is required.
        field = self.field_class(**self.create_params(required=True))
        setattr(field, 'to_internal_value', to_internal_value)
        res = field.run_validation(123)
        assert res == 123, '`.run_validation()` must return 123.'

        # Now we try to make validator work.
        try:
            field.run_validation(None)
            self.fail('`.run_validation()` must throw as exception `ValidationError`.')
        except ValidationError:
            pass

    def test_run_validators(self):
        """
        Testing work validators

        """
        # Check without validators.
        field = self.field_class(**self.create_params(required=False, validators=[]))
        field.run_validators(123)

        # Check with default validators.
        field = self.field_class(**self.create_params(required=True, validators=[]))
        field.run_validators(123)
        try:
            field.run_validators(None)
            self.fail('`.run_validators()` must throw as exception `ValidationError`.')
        except ValidationError:
            pass

        # Check with custom validators.
        def test_validator(value):
            if value == 1:
                raise ValidationError(1)

        field = self.field_class(**self.create_params(required=True, validators=[test_validator]))
        field.run_validators(10)
        try:
            field.run_validators(1)
            self.fail('`.run_validators()` must throw as exception `ValidationError`.')
        except ValidationError:
            pass


class CharFieldTest(BaseFieldTestCase):
    """
    Testing CharField.

    """
    field_class = CharField
    abstract_methods = {}  # Custom abstract methods.
    field_error_messages = {
        'invalid': None,
        'blank': None,
        'min_length': None,
        'max_length': None
    }  # Custom errors list.
    to_representation_cases = (
        {'data': {'value': '123'}, 'return': '123'},
        {'data': {'value': 123}, 'return': '123'},
        {'data': {'value': 'qwe'}, 'return': 'qwe'}
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': '123'}, 'return': '123'},
        {'data': {'data': True}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)}
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': '123'}, 'return': '123'},
        {'data': {'data': 123}, 'return': '123'},
        {'data': {'data': 'qwe'}, 'return': 'qwe'},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': ''}, 'params': {'allow_blank': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ''}, 'params': {'allow_blank': True}, 'return': ''},
        {'data': {'data': '   '}, 'params': {'allow_blank': True, 'trim_whitespace': True}, 'return': ''},
        {'data': {'data': '   '}, 'params': {'allow_blank': False, 'trim_whitespace': True}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.run_validation()`.

    def test_init(self):
        """
        Testing create.

        """
        params = dict(max_length=10, min_length=20, trim_whitespace=False, allow_blank=True, required=True)
        field = self.field_class(**params)

        # Look at validators.
        assert len(field.validators) == 3, '`.validators` must have length 3, reality {}'.format(len(field.validators))
        for v in field.validators:
            assert isinstance(v, (RequiredValidator, MaxLengthValidator, MinLengthValidator)), \
                'Validator must be `RequiredValidator, MaxLengthValidator, MinLengthValidator`, reality `{}`'.format(
                    type(v)
                )

        # Look that without them too it is possible.
        params.update(max_length=None, min_length=None)
        field = self.field_class(**params)
        assert len(field.validators) == 1, '`.validators` must have length 1, reality {}'.format(len(field.validators))
        for v in field.validators:
            assert isinstance(v, RequiredValidator), 'Validator must be `RequiredValidator`, reality `{}`'.format(type(v))


class TestIntegerField(BaseFieldTestCase):
    """
    Testing IntegerField.

    """
    field_class = IntegerField
    abstract_methods = {}  # Custom abstract methods.
    field_error_messages = {
        'invalid': None,
        'min_value': None,
        'max_value': None,
        'max_string_length': None
    }  # Custom errors list.
    to_representation_cases = (
        {'data': {'value': 123}, 'return': 123},
        {'data': {'value': '123'}, 'return': 123},
        {'data': {'value': 'qwe'}, 'exceptions': (ValueError,)},
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': '123.0'}, 'return': 123},
        {'data': {'data': '123.1'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': '123.0'}, 'return': 123},
        {'data': {'data': '123.1'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'min_value': 5}, 'return': 10},
        {'data': {'data': 10}, 'params': {'min_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'min_value': 11}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11, 'min_value': 5}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 10, 'min_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 5, 'min_value': 5}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.run_validation()`.


class TestFloatField(BaseFieldTestCase):
    """
    Testing FloatField.

    """
    field_class = FloatField
    abstract_methods = {}  # Custom abstract methods.
    field_error_messages = {
        'invalid': None,
        'min_value': None,
        'max_value': None,
        'max_string_length': None
    }  # Custom errors list.
    to_representation_cases = (
        {'data': {'value': 123}, 'return': 123.0},
        {'data': {'value': '123'}, 'return': 123.0},
        {'data': {'value': 'qwe'}, 'exceptions': (ValueError,)},
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': 123}, 'return': 123.0},
        {'data': {'data': '123'}, 'return': 123.0},
        {'data': {'data': '123.0'}, 'return': 123.0},
        {'data': {'data': '123.1'}, 'return': 123.1},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'return': 0.0},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': 123}, 'return': 123.0},
        {'data': {'data': '123'}, 'return': 123.0},
        {'data': {'data': '123.0'}, 'return': 123.0},
        {'data': {'data': '123.1'}, 'return': 123.1},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'return': 0.0},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'min_value': 5}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'min_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'min_value': 11}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11, 'min_value': 5}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 10, 'min_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 5, 'min_value': 5}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.run_validation()`.


class TestBooleanField(BaseFieldTestCase):
    """
    Testing BooleanField.

    """
    field_class = BooleanField
    abstract_methods = {}  # Custom abstract methods.
    field_error_messages = {'invalid': None}
    to_representation_cases = (
        {'data': {'value': True}, 'return': True},
        {'data': {'value': False}, 'return': False},
        {'data': {'value': None}, 'return': None},
        {'data': {'value': 'Yes'}, 'return': True},
        {'data': {'value': 1}, 'return': True},
        {'data': {'value': 'No'}, 'return': False},
        {'data': {'value': 0}, 'return': False},
        {'data': {'value': 'null'}, 'return': None},
        {'data': {'value': ''}, 'return': None},
        {'data': {'value': '100'}, 'return': True}
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': True}, 'return': True},
        {'data': {'data': False}, 'return': False},
        {'data': {'data': None}, 'return': None},
        {'data': {'data': 'Yes'}, 'return': True},
        {'data': {'data': 1}, 'return': True},
        {'data': {'data': 'No'}, 'return': False},
        {'data': {'data': 0}, 'return': False},
        {'data': {'data': 'null'}, 'return': None},
        {'data': {'data': ''}, 'return': None},
        {'data': {'data': '100'}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': True}, 'return': True},
        {'data': {'data': False}, 'return': False},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': 'Yes'}, 'return': True},
        {'data': {'data': 1}, 'return': True},
        {'data': {'data': 'No'}, 'return': False},
        {'data': {'data': 0}, 'return': False},
        {'data': {'data': 'null'}, 'params': {'required': False}, 'return': None},
        {'data': {'data': ''}, 'params': {'required': False}, 'return': None},
        {'data': {'data': '100'}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.run_validation()`.


class TestListField(BaseFieldTestCase):
    """
    Testing ListField.

    """
    field_class = ListField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {
        'child': CharField(required=False)
    }  # Required arguments for creating a field.
    field_error_messages = {
        'not_a_list': None,
        'empty': None,
        'min_length': None,
        'max_length': None
    }
    _fields_vals = {
        'required': True, 'default': None, 'label': None, 'validators': [],
        'error_messages': {}, 'default_error_messages': {}, 'default_validators': [],
        'child': CharField()
    }

    to_representation_cases = (
        {'data': {'value': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'value': [123, 123, 123]}, 'return': ['123', '123', '123']},
        {'data': {'value': [True, True, True]}, 'return': ['True', 'True', 'True']},
        {'data': {'value': ['123', 123, True, None]}, 'return': ['123', '123', 'True', None]},
        {'data': {'value': None}, 'return': []},
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': ''}, 'exceptions': (ValidationError,)},
        {'data': {'data': {}}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': []}, 'params': {'allow_empty': True}, 'return': []},
        {'data': {'data': []}, 'params': {'allow_empty': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'data': [123, 123, 123]}, 'return': ['123', '123', '123']},
        # Errors will be here, because CharField does not get True False No as a string.
        {'data': {'data': [True, True, True]}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', 123, True, None]}, 'exceptions': (ValidationError,)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': ''}, 'exceptions': (ValidationError,)},
        {'data': {'data': {}}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': []}, 'params': {'allow_empty': True}, 'return': []},
        {'data': {'data': []}, 'params': {'allow_empty': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'data': [123, 123, 123]}, 'return': ['123', '123', '123']},
        # Errors will be here, because CharField does not get True False No as a string.
        {'data': {'data': [True, True, True]}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', 123, True, None]}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 2, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 2}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 5, 'max_length': 10}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 3, 'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 2}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, True, '1']}, 'params': {'child': None}, 'return': [1, True, '1']}  # Check empty child field.
    )  # Cases, to test the performance of `.run_validation()`.


class TestTimeField(BaseFieldTestCase):
    """
    Testing TimeField.

    """
    field_class = TimeField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.
    field_error_messages = {
        'invalid': None,
        'time': None
    }

    to_representation_cases = (
        {'data': {'value': datetime.time()}, 'return': '00:00:00'},
        {'data': {'value': datetime.time(10, 10)}, 'return': '10:10:00'},
        {'data': {'value': '10:10:10'}, 'return': '10:10:10'},
        {'data': {'value': 'test'}, 'return': 'test'},  # TODO: fix
        {'data': {'value': None}, 'return': None},
        {"data": {'value': type('object', (object,), {})}, 'exceptions': (AttributeError,)},  # Not valid object.
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': '00:00:00'}, 'return': datetime.time(0, 0, 0)},
        {'data': {'data': '10:10:10'}, 'return': datetime.time(10, 10, 10)},
        {'data': {'data': '10:10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': datetime.time()}, 'return': datetime.time()},
        {'data': {'data': datetime.time(10, 10)}, 'return': datetime.time(10, 10)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': '00:00:00'}, 'return': datetime.time(0, 0, 0)},
        {'data': {'data': '10:10:10'}, 'return': datetime.time(10, 10, 10)},
        {'data': {'data': '10:10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': datetime.time()}, 'return': datetime.time()},
        {'data': {'data': datetime.time(10, 10)}, 'return': datetime.time(10, 10)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': None}, 'params': {'default': datetime.time()}, 'return': datetime.time()},
    )  # Cases, to test the performance of `.run_validation()`.


class TestDateField(BaseFieldTestCase):
    """
    Testing DateField.

    """
    field_class = DateField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.
    field_error_messages = {
        'invalid': None,
        'datetime': None
    }

    to_representation_cases = (
        {'data': {'value': datetime.date(2018, 1, 1)}, 'return': '2018-01-01'},
        {'data': {'value': datetime.date(2018, 10, 10)}, 'return': '2018-10-10'},
        {'data': {'value': datetime.date(2018, 10, 10)}, 'params': {'format': '%d.%m.%Y'}, 'return': '10.10.2018'},
        {'data': {'value': datetime.datetime.now()}, 'exceptions': (AssertionError,)},
        {'data': {'value': 'test'}, 'return': 'test'},  # TODO: fix
        {'data': {'value': None}, 'return': None},
        {"data": {'value': type('object', (object,), {})}, 'exceptions': (AttributeError,)},  # Not valid object.
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': '2018-01-01'}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': datetime.date(2018, 1, 1)}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': '2018-10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': '1.1.2018'}, 'params': {'input_format': '%d.%m.%Y'}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': datetime.datetime.now()}, 'exceptions': (ValidationError,)},
        {'data': {'data': '2018-10'}, 'params': {'input_format': '%Y-%m'}, 'return': datetime.date(2018, 10, 1)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': '2018-01-01'}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': datetime.date(2018, 1, 1)}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': '2018-10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': '1.1.2018'}, 'params': {'input_format': '%d.%m.%Y'}, 'return': datetime.date(2018, 1, 1)},
        {'data': {'data': datetime.datetime.now()}, 'exceptions': (ValidationError,)},
        {'data': {'data': '2018-10'}, 'params': {'input_format': '%Y-%m'}, 'return': datetime.date(2018, 10, 1)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': None}, 'params': {'default': datetime.date(2018, 1, 1)}, 'return': datetime.date(2018, 1, 1)},
    )  # Cases, to test the performance of `.run_validation()`.


class TestDateTimeField(BaseFieldTestCase):
    """
    Testing DateTimeField.

    """
    field_class = DateTimeField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.
    field_error_messages = {
        'invalid': None,
        'date': None,
    }
    __now = datetime.datetime.now()
    __now_for_test = datetime.datetime(__now.year, __now.month, __now.day, __now.hour, __now.minute, __now.second)

    to_representation_cases = (
        {'data': {'value': datetime.datetime(2018, 1, 1)}, 'return': '2018-01-01 00:00:00'},
        {'data': {'value': datetime.datetime(2018, 10, 10)}, 'return': '2018-10-10 00:00:00'},
        {'data': {'value': datetime.datetime(2018, 10, 10)}, 'params': {'format': '%d.%m.%Y'}, 'return': '10.10.2018'},
        {'data': {'value': datetime.datetime(2018, 1, 1, 1, 1, 1)}, 'return': '2018-01-01 01:01:01'},
        {'data': {'value': datetime.datetime(2018, 1, 1, 1, 1, 1)}, 'params': {'format': '%d.%m.%Y %H-%M-%S'}, 'return': '01.01.2018 01-01-01'},
        {'data': {'value': 'test'}, 'return': 'test'},  # TODO: fix
        {'data': {'value': None}, 'return': None},
        {"data": {'value': type('object', (object,), {})}, 'exceptions': (AttributeError,)},  # Not valid object.
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': '2018-01-01 00:00:00'}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': datetime.datetime(2018, 1, 1)}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': '2018-10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': '1.1.2018'}, 'params': {'input_format': '%d.%m.%Y'}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': __now_for_test.strftime(DateTimeField.input_format)}, 'return': __now_for_test},
        {'data': {'data': '2018-10'}, 'params': {'input_format': '%Y-%m'}, 'return': datetime.datetime(2018, 10, 1)},
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': '2018-01-01 00:00:00'}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': datetime.datetime(2018, 1, 1)}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': '2018-10'}, 'exceptions': (ValidationError,)},
        {'data': {'data': '1.1.2018'}, 'params': {'input_format': '%d.%m.%Y'}, 'return': datetime.datetime(2018, 1, 1)},
        {'data': {'data': __now_for_test.strftime(DateTimeField.input_format)}, 'return': __now_for_test},
        {'data': {'data': '2018-10'}, 'params': {'input_format': '%Y-%m'}, 'return': datetime.datetime(2018, 10, 1)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': None}, 'params': {'default': datetime.datetime(2018, 1, 1)}, 'return': datetime.datetime(2018, 1, 1)},
    )  # Cases, to test the performance of `.run_validation()`.


class TestJsonField(BaseFieldTestCase):
    """
    Testing JsonField.

    """
    field_class = JsonField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.
    field_error_messages = {
        'invalid': None,
    }

    to_representation_cases = (
        {'data': {'value': '123'}, 'return': '"123"'},
        {'data': {'value': 123}, 'return': '123'},
        {'data': {'value': {}}, 'return': '{}'},
        {'data': {'value': []}, 'return': '[]'},
        {'data': {'value': {'123': 123}}, 'return': '{"123": 123}'},
        {'data': {'value': {'123': [123, '123']}}, 'return': '{"123": [123, "123"]}'},
        {'data': {'value': lambda: None}, 'exceptions': (ValidationError,)},
        {'data': {'value': {123: 123}}, 'return': '{"123": 123}'}
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': []}, 'return': []},
        {'data': {'data': {123: 123}}, 'return': {123: 123}},
        {'data': {'data': [123]}, 'return': [123]},
        {'data': {'data': {123: [123]}}, 'return': {123: [123]}},
        {'data': {'data': [{123: 123}]}, 'return': [{123: 123}]},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': 'asd'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 123}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)}
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': []}, 'return': []},
        {'data': {'data': {123: 123}}, 'return': {123: 123}},
        {'data': {'data': [123]}, 'return': [123]},
        {'data': {'data': {123: [123]}}, 'return': {123: [123]}},
        {'data': {'data': [{123: 123}]}, 'return': [{123: 123}]},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': 'asd'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 123}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},  # TODO: FIXME
    )  # Cases, to test the performance of `.run_validation()`.


class TestDictField(BaseFieldTestCase):
    """
    Testing DictField.

    """
    field_class = DictField
    abstract_methods = {}  # Custom abstract methods.
    requirement_arguments_for_field = {}  # Required arguments for creating a field.
    field_error_messages = {
        'not_a_dict': None,
    }

    to_representation_cases = (
        {'data': {'value': {}}, 'return': {}},
        {'data': {'value': {'123': 123}}, 'return': {'123': 123}},
        {'data': {'value': {'123': [123, '123']}}, 'return': {'123': [123, '123']}},
        {'data': {'value': '123'}, 'exceptions': (AttributeError,)},
        {'data': {'value': 123}, 'exceptions': (AttributeError,)},
        {'data': {'value': lambda: None}, 'exceptions': (AttributeError,)},
        {'data': {'value': {123: 123}}, 'return': {'123': 123}},
        {'data': {'value': {123: [123]}}, 'params': {'child': IntegerField()}, 'exceptions': (TypeError,)}
    )  # Cases, to test the performance of `.to_representation()`.
    to_internal_value_cases = (
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': {123: 123}}, 'return': {'123': 123}},
        {'data': {'data': {123: [123]}}, 'return': {'123': [123]}},
        {'data': {'data': '123'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'asd'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 123}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': {123: [123]}}, 'params': {'child': IntegerField()}, 'exceptions': (ValidationError,)}
    )  # Cases, to test the performance of `.to_internal_value()`.
    run_validation_cases = (
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': {123: 123}}, 'return': {'123': 123}},
        {'data': {'data': {123: [123]}}, 'return': {'123': [123]}},
        {'data': {'data': '123'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'asd'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 123}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},  # TODO: FIXME
        {'data': {'data': {123: [123]}}, 'params': {'child': IntegerField()}, 'exceptions': (ValidationError,)}
    )  # Cases, to test the performance of `.run_validation()`.


class TestSerializerMethodField(TestCase):
    """
    Testing SerializerMethodField.

    """
    def test_default_validation(self):
        """
        Testing default methods.

        """
        ser = SerializerMethodFieldDefault(data={'test': 'test'})
        ser.is_valid()
        assert ser.validated_data['test'] == 'test', 'Expected `test`. Reality: `{}`.'.format(ser.validated_data['test'])

        ser = SerializerMethodFieldDefault(data={'test': 'test'})
        setattr(ser, 'pop_test', lambda *args: None)
        ser.is_valid()
        assert ser.validated_data['test'] is None, 'Expected `None`. Reality: `{}`.'.format(ser.validated_data['test'])

        ser = SerializerMethodFieldDefault(data={'test': 'test'})
        setattr(ser, 'pop_test', lambda *args: 123)
        ser.is_valid()
        assert ser.validated_data['test'] == 123, 'Expected `123`. Reality: `{}`.'.format(ser.validated_data['test'])

    def test_default_serializing(self):
        """
        Testing serializing object.

        """
        # Standard value.
        obj = type('Object', (object,), {'test': 'test'})
        ser = SerializerMethodFieldDefault(instance=obj)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] == obj, 'Expected value `test`. Reality: `{}`.'.format(ser.data['test'])

        ser = SerializerMethodFieldDefault(instance=obj)
        setattr(ser, 'get_test', lambda *args: None)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] is None, 'Expected value `None`. Reality: `{}`.'.format(ser.data['test'])

        ser = SerializerMethodFieldDefault(instance=obj)
        setattr(ser, 'get_test', lambda *args: 123)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] == 123, 'Expected value `123`. Reality: `{}`.'.format(ser.data['test'])

    def test_single_method_validation(self):
        """
        Testing single method.

        """
        ser = SerializerMethodFieldSingle(data={'test': 'test'})
        ser.is_valid()
        assert ser.validated_data['test'] == 'test', 'Expected `test`. Reality: `{}`.'.format(ser.validated_data['test'])

        ser = SerializerMethodFieldSingle(data={'test': 'test'})
        setattr(ser, 'test_test', lambda *args: None)
        ser.is_valid()
        assert ser.validated_data['test'] is None, 'Expected `None`. Reality: `{}`.'.format(ser.validated_data['test'])

        ser = SerializerMethodFieldSingle(data={'test': 'test'})
        setattr(ser, 'test_test', lambda *args: 123)
        ser.is_valid()
        assert ser.validated_data['test'] == 123, 'Expected `123`. Reality: `{}`.'.format(ser.validated_data['test'])

        ser = SerializerMethodFieldSingle(data={'test': 'test'})
        setattr(ser, 'pop_test', lambda *args: 123)
        ser.is_valid()
        assert ser.validated_data['test'] == 'test', 'Expected `test`. Reality: `{}`.'.format(ser.validated_data['test'])

    def test_single_method_serializing(self):
        """
        Testing serializing object.

        """
        # Standard value.
        obj = type('Object', (object,), {'test': 'test'})
        ser = SerializerMethodFieldSingle(instance=obj)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] == obj, 'Expected value `test`. Reality: `{}`.'.format(ser.data['test'])

        ser = SerializerMethodFieldSingle(instance=obj)
        setattr(ser, 'test_test', lambda *args: None)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] is None, 'Expected value `None`. Reality: `{}`.'.format(ser.data['test'])

        ser = SerializerMethodFieldSingle(instance=obj)
        setattr(ser, 'test_test', lambda *args: 123)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] == 123, 'Expected value `123`. Reality: `{}`.'.format(ser.data['test'])

        ser = SerializerMethodFieldSingle(instance=obj)
        setattr(ser, 'get_test', lambda *args: 123)
        assert isinstance(ser.data, dict), 'Expected type: `dict`. Reality: `{}`.'.format(type(ser.data))
        assert len(ser.data) == 1, 'Expected single value in data. Reality: `{}`.'.format(ser.data)
        assert ser.data['test'] == obj, 'Expected value `test`. Reality: `{}`.'.format(ser.data['test'])
