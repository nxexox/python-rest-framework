"""
Testing validators.

"""
import unittest

import six

from rest_framework.serializers.validators import (
    RegexValidator, BaseValidator, RequiredValidator, MinLengthValidator, MaxLengthValidator,
    MinValueValidator, MaxValueValidator
)
from rest_framework.serializers.exceptions import ValidationError


class ValidatorTestCases(unittest.TestCase):
    """
    Cases testing on validators.

    """
    validator_class = BaseValidator

    cases = (
        # {'init': {}, 'data': None, 'message': ''}
        # `init` - params to __init__ method, `data` - data for validation,
        # `message` - message from exceptions, if exceptions raises.
        # {'init': {}, 'data': None},
        {},
    )

    def __get_serializer_repr(self, case):
        return '{}({})'.format(
            self.validator_class.__class__.__name__,
            ', '.join(map(lambda x: '%s=%s' % (str(x[0]), str(x[1])), six.iteritems(case.get('init', {}))))
        )

    def __test_case(self, case):
        """
        Testing current case.

        :param dict case: Current case.

        """
        if issubclass(self.validator_class, MinLengthValidator):
            print()

        validator = self.validator_class(**case.get('init', {}))

        try:
            validator(case['data'])
            if case.get('message', None):
                self.fail('{} must be raise ValidationError. Case: `{}`.'.format(
                    self.__get_serializer_repr(case), case
                ))
        except ValidationError as e:
            msg = case.get('message', None)
            if not msg:
                self.fail('{} raise ValidationError. Expected valid value. Case: `{}`.'.format(
                    self.__get_serializer_repr(case), case
                ))
            if msg != e.detail:
                self.fail('Error message not equal expected on validator {}. MSG: `{}`. Case: `{}`.'.format(
                    self.__get_serializer_repr(case),
                    e.detail,
                    msg
                ))

    def test_cases(self):
        """
        Testing all cases.

        """
        for case in self.cases:
            # Skip case.
            if not case:
                continue

            try:
                # Run test case.
                self.__test_case(case)
            except Exception as e:
                self.fail(
                    'During the inspection of the case `{}` an unexpected error occurred: `{}: {}`'.format(
                        case, e.__class__.__name__, e
                    ))


class RequiredValidatorTestCase(ValidatorTestCases):
    """
    Testing Required validator.

    """
    validator_class = RequiredValidator
    cases = (
        {'data': None, 'message': 'This field is required.'},
        {'init': {'message': 'test'}, 'data': None, 'message': 'test'},
        {'data': False},
        {'data': ''},
        {'data': 0},
        {'data': 'data'}
    )


class MinLengthValidatorTestCase(ValidatorTestCases):
    """
    Testing MinLengthValidator.

    """
    validator_class = MinLengthValidator
    cases = (
        {'init': {'min_length': 10}, 'data': [], 'message': 'The value must be longer than 10.'},
        {'init': {'min_length': 2}, 'data': [1, 1]},
        {'init': {'min_length': 2}, 'data': [1, 1, 1, 1]},
        {'init': {'min_length': 2}, 'data': [1], 'message': 'The value must be longer than 2.'},
        {'init': {'min_length': 3, 'message': 'test-{min_length}'}, 'data': [], 'message': 'test-3'}
    )


class MaxLengthValidatorTestCase(ValidatorTestCases):
    """
    Testing MaxLengthValidator.

    """
    validator_class = MaxLengthValidator
    cases = (
        {'init': {'max_length': 10}, 'data': []},
        {'init': {'max_length': 2}, 'data': [1, 1]},
        {'init': {'max_length': 2}, 'data': [1, 1, 1, 1], 'message': 'The value must be shorter than 2.'},
        {'init': {'max_length': 2}, 'data': [1, 1, 1], 'message': 'The value must be shorter than 2.'},
        {'init': {'max_length': 2, 'message': 'test-{max_length}'}, 'data': [1, 1, 1], 'message': 'test-2'},
    )


class MinValueValidatorTestCase(ValidatorTestCases):
    """
    Testing MinValueValidator.

    """
    validator_class = MinValueValidator
    cases = (
        {'init': {'min_value': 10}, 'data': 13},
        {'init': {'min_value': 2}, 'data': 2},
        {'init': {'min_value': 2}, 'data': 1, 'message': 'The value must be greater than or equal to 2.'},
        {'init': {'min_value': 2, 'message': 'test-{min_value}'}, 'data': 1, 'message': 'test-2'},
    )


class MaxValueValidatorTestCase(ValidatorTestCases):
    """
    Testing MaxValueValidator.

    """
    validator_class = MaxValueValidator
    cases = (
        {'init': {'max_value': 10}, 'data': 3},
        {'init': {'max_value': 2}, 'data': 2},
        {'init': {'max_value': 2}, 'data': 10, 'message': 'The value must be less than or equal to 2.'},
        {'init': {'max_value': 2, 'message': 'test-{max_value}'}, 'data': 10, 'message': 'test-2'},
    )


class RegexValidatorTestCase(ValidatorTestCases):
    """
    Testing RegexValidator.

    """
    validator_class = RegexValidator
    cases = (
        {'init': {'regex': r'\d+'}, 'data': '3'},
        {'init': {'regex': r'\d+'}, 'data': '3124124'},
        {'init': {'regex': r'\d+'}, 'data': 'asdasd', 'message': 'Enter a valid value.'},
        {'init': {'regex': r'\d+', 'message': 'test'}, 'data': 'test', 'message': 'test'},
        {'init': {'regex': r'\d+', 'inverse_match': True}, 'data': 'test'}
    )
