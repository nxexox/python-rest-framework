"""
Classes for pagination objects in response.

"""
import abc

import six

from rest_framework.utils.decorators import copy_methods_signature


class BasePaginatorAbstract(six.with_metaclass(abc.ABCMeta, object)):
    """
    Paginator for base class.

    """
    def __init__(self, objects):
        self.objects = objects

    @abc.abstractmethod
    def get_paginate_data(self, *args, **kwargs):
        """
        Get paginate data, page_size, count_page and etc.

        :return: Paginate data dict.
        :rtype: dict

        Examples:
            return {limit: 10, offset: 10, count: 100}
            return {after: 'hash_code', before: 'hash_code', count_objects: 10}

        """
        pass

    @abc.abstractmethod
    def get_objects_data(self):
        """
        Get paginate objects data.

        :return: Pagination objects dict
        :rtype: dict

        Examples:
            return {'result': self.objects}
            return {'objects': self.objects}

        """
        pass

    def paginate(self, *args, **kwargs):
        """
        Paginate method. Return result paginate dict.

        :return: Result paginate data
        :rtype: dict

        """
        result = {}
        result.update(self.get_paginate_data(*args, **kwargs))
        result.update(self.get_objects_data())
        return result


class LimitOffsetGetPaginateDataMixin(BasePaginatorAbstract):
    """
    Mixin for limit offset pagination.

    """
    def get_paginate_data(self, limit=10, offset=0, count=None):
        """
        Get paginate data for limit offset pagination.

        :return: Paginate data dict. {'limit': limit, 'offset': offset, count: count}
        :rtype: dict

        """
        return dict(limit=limit, offset=offset, count=count)


class ResultGetObjectsDataPaginatorMixin(BasePaginatorAbstract):
    """
    Mixin for return result from get_objects_data.

    """
    def get_objects_data(self):
        """
        Get paginate objects data.

        :return: Pagination objects dict. {'result': objects}
        :rtype: dict

        """
        return dict(result=self.objects)


class ObjectsGetObjectsDataPaginatorMixin(BasePaginatorAbstract):
    """
    Mixin for return result from get_objects_data.

    """
    def get_objects_data(self):
        """
        Get paginate objects data.

        :return: Pagination objects dict. {'objects': objects}
        :rtype: dict

        """
        return dict(objects=self.objects)


class ItemsGetObjectsDataPaginatorMixin(BasePaginatorAbstract):
    """
    Mixin for return result from get_objects_data.

    """
    def get_objects_data(self):
        """
        Get paginate objects data.

        :return: Pagination objects dict. {'items': objects}
        :rtype: dict

        """
        return dict(items=self.objects)


@copy_methods_signature({'get_paginate_data': 'paginate'})
class LimitOffsetResultPaginator(LimitOffsetGetPaginateDataMixin, ResultGetObjectsDataPaginatorMixin,
                                 BasePaginatorAbstract):
    """
    Limit offset result paginator.

    """
    pass


@copy_methods_signature({'get_paginate_data': 'paginate'})
class LimitOffsetObjectsPaginator(LimitOffsetGetPaginateDataMixin, ObjectsGetObjectsDataPaginatorMixin,
                                  BasePaginatorAbstract):
    """
    Limit offset objects paginator.

    """
    pass


@copy_methods_signature({'get_paginate_data': 'paginate'})
class LimitOffsetItemsPaginator(LimitOffsetGetPaginateDataMixin, ItemsGetObjectsDataPaginatorMixin,
                                BasePaginatorAbstract):
    """
    Limit offset items paginator.

    """
    pass
