"""
Testing views mixins.

"""
import unittest
from functools import namedtuple

from rest_framework.views.mixins import (
    GetSerializerMixin, GetResponseMixin
)
from rest_framework.views.paginations import LimitOffsetObjectsPaginator

from tests.serializers_for_tests import SerializerPrimitiveField


Response = namedtuple('Response', ('data', 'status', 'content_type'))


class ForTests(object):
    @property
    def request_object(self):
        """
        Get request object.

        :return: Request object.
        :rtype:

        """
        return None

    @property
    def current_request_method(self):
        """
        Get current string request method name.

        :return: Request method name
        :rtype: str

        """
        return 'get'


class GetSerializerMixinTestCase(unittest.TestCase):
    """
    Tests for GetSerializerMixin.

    """
    serializer_for_tests = SerializerPrimitiveField

    def test_empty_serializer(self):
        class ForTest(ForTests, GetSerializerMixin):
            serializer_classes = {}

        mixin = ForTest()

        self.assertIsNone(mixin.get_request_serializer())
        self.assertIsNone(mixin.get_response_serializer())
        self.assertIsNone(mixin.get_serializer('in'))
        self.assertIsNone(mixin.get_serializer('out'))

    def test_get_serializer(self):
        class ForTest(ForTests, GetSerializerMixin):
            serializer_classes = {}

        mixin = ForTest()

        self.assertIsNone(mixin.get_serializer('in'))
        self.assertIsNone(mixin.get_serializer('out'))
        self.assertIsNone(mixin.get_serializer('IN'))
        self.assertIsNone(mixin.get_serializer('OUT'))
        self.assertIsNone(mixin.get_serializer('In'))
        self.assertIsNone(mixin.get_serializer('Out'))
        self.assertIsNone(mixin.get_serializer('iN'))
        self.assertIsNone(mixin.get_serializer('oUt'))
        self.assertIsNone(mixin.get_serializer('not_valid_key'))

    def test_get_single_serializer(self):
        class ForTest(ForTests, GetSerializerMixin):
            serializer_classes = {'get': self.serializer_for_tests}

        mixin = ForTest()

        assert issubclass(mixin.get_serializer('in'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('out'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('IN'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('OUT'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('In'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('Out'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('iN'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('oUt'), self.serializer_for_tests)
        self.assertIsNone(mixin.get_serializer('not_valid_key'))

    def test_full_serializers(self):
        class ForTest(ForTests, GetSerializerMixin):
            serializer_classes = {
                'get': {'in': self.serializer_for_tests, 'out': self.serializer_for_tests}
            }

        mixin = ForTest()

        assert issubclass(mixin.get_serializer('in'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('out'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('IN'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('OUT'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('In'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('Out'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('iN'), self.serializer_for_tests)
        assert issubclass(mixin.get_serializer('oUt'), self.serializer_for_tests)
        self.assertIsNone(mixin.get_serializer('not_valid_key'))


class GetResponseMixinTestCase(unittest.TestCase):
    """
    Test GetResponseMixin.

    """
    def test_get_response(self):
        try:
            class ForTest(ForTests, GetResponseMixin):
                pass
            # TODO: Not working
            # self.fail('No reaction on empty response_class attribute.')
        except AttributeError:
            pass

        def get_response(data, status, content_type='application/json'):
            return Response(data, status, content_type)

        class ForTest(ForTests, GetResponseMixin):
            response_class = get_response

        mixin = ForTest()

        resp = mixin.get_response({'test': 'test'}, status_code=400, is_serialized=False)
        self.assertEqual(resp.data, {'test': 'test'})
        self.assertEqual(resp.status, 400)

    def test_get_list_response(self):
        try:
            class ForTest(ForTests, GetResponseMixin):
                pass
            # TODO: Not working
            # self.fail('No reaction on empty response_class attribute.')
        except AttributeError:
            pass

        def get_response(data, status, content_type='application/json'):
            return Response(data, status, content_type)

        class ForTest(ForTests, GetResponseMixin):
            response_class = get_response
            pagination_class = LimitOffsetObjectsPaginator

        mixin = ForTest()

        resp = mixin.get_list_response(
            [{'test': 'test'}],
            status_code=400, limit=1, offset=0, count=1,
            is_serialized=False
        )
        self.assertEqual(
            resp.data, {
                'limit': 1, 'offset': 0, 'count': 1, 'objects': [{'test': 'test'}]
            }
        )
        self.assertEqual(resp.status, 400)

