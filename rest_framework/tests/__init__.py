import unittest

from rest_framework.tests.test_fields import *
from rest_framework.tests.test_serializers import *
from rest_framework.tests.test_validators import *

__all__ = (
    # test fields
    'BaseFieldTestCase', 'CharFieldTest', 'TestIntegerField', 'TestFloatField', 'TestBooleanField',
    'TestListField',

    # test serializers
    'BaseSerializerTestClass', 'SerializerTestClass', 'SerializerUserTestCase', 'SerializerSingleMixinTestCase',
    'SerializerManyMixinTestCase', 'SerializerRequiredMixinTestCase',
)

if __name__ == '__main__':
    unittest.main()
