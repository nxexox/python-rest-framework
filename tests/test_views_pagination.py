"""
Testing views pagination.

"""
import unittest

from rest_framework.views.paginations import (
    BasePaginatorAbstract, LimitOffsetGetPaginateDataMixin, ResultGetObjectsDataPaginatorMixin,
    ObjectsGetObjectsDataPaginatorMixin, ItemsGetObjectsDataPaginatorMixin, LimitOffsetResultPaginator,
    LimitOffsetObjectsPaginator, LimitOffsetItemsPaginator
)


class LimitOffsetGetPaginateDataMixinTestCase(unittest.TestCase):
    def test(self):
        class Paginator(LimitOffsetGetPaginateDataMixin):
            def get_objects_data(self):
                return {}

        paginator = Paginator([1, 2])
        self.assertEqual(paginator.paginate(), dict(limit=10, offset=0, count=None))
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(limit=1, offset=0, count=None)
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(limit=1, offset=1, count=None)
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(limit=1, offset=1, count=10)
        )


class ResultGetObjectsDataPaginatorMixinTestCase(unittest.TestCase):
    def test(self):
        class Paginator(ResultGetObjectsDataPaginatorMixin):
            def get_paginate_data(self, *args, **kwargs):
                return {}

        paginator = Paginator([1, 2])
        self.assertEqual(paginator.paginate(), dict(result=[1, 2]))
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(result=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(result=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(result=[1, 2])
        )


class ObjectsGetObjectsDataPaginatorMixinTestCase(unittest.TestCase):
    def test(self):
        class Paginator(ObjectsGetObjectsDataPaginatorMixin):
            def get_paginate_data(self, *args, **kwargs):
                return {}

        paginator = Paginator([1, 2])
        self.assertEqual(paginator.paginate(), dict(objects=[1, 2]))
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(objects=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(objects=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(objects=[1, 2])
        )


class ItemsGetObjectsDataPaginatorMixinTestCase(unittest.TestCase):
    def test(self):
        class Paginator(ItemsGetObjectsDataPaginatorMixin):
            def get_paginate_data(self, *args, **kwargs):
                return {}

        paginator = Paginator([1, 2])
        self.assertEqual(paginator.paginate(), dict(items=[1, 2]))
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(items=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(items=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(items=[1, 2])
        )


class LimitOffsetResultPaginatorTestCase(unittest.TestCase):
    def test(self):
        paginator = LimitOffsetResultPaginator([1, 2])

        self.assertEqual(
            paginator.paginate(),
            dict(limit=10, offset=0, count=None, result=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(limit=1, offset=0, count=None, result=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(limit=1, offset=1, count=None, result=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(limit=1, offset=1, count=10, result=[1, 2])
        )


class LimitOffsetObjectsPaginatorestCase(unittest.TestCase):
    def test(self):
        paginator = LimitOffsetObjectsPaginator([1, 2])

        self.assertEqual(
            paginator.paginate(),
            dict(limit=10, offset=0, count=None, objects=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(limit=1, offset=0, count=None, objects=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(limit=1, offset=1, count=None, objects=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(limit=1, offset=1, count=10, objects=[1, 2])
        )


class LimitOffsetItemsPaginatorTestCase(unittest.TestCase):
    def test(self):
        paginator = LimitOffsetItemsPaginator([1, 2])

        self.assertEqual(
            paginator.paginate(),
            dict(limit=10, offset=0, count=None, items=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1),
            dict(limit=1, offset=0, count=None, items=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1),
            dict(limit=1, offset=1, count=None, items=[1, 2])
        )
        self.assertEqual(
            paginator.paginate(limit=1, offset=1, count=10),
            dict(limit=1, offset=1, count=10, items=[1, 2])
        )
