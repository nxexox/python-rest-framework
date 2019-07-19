# Pagination

`Python-Rest-Framework` provides classes for pagination. These classes are used directly in [`GetResponseMixin`][GetResponseMixin].
But they can be used independently for any purpose.

Classes themselves do not perform pagination, they only form the correct `JSON`, for the correct response to the client.

**All Mixins can be found here:**
```python
from rest_framework.views.paginations import *
```

---

# Paginator Classes

Full classes for pagination.
`Paginators` accept the data themselves in their constructor.
Then the `.paginate()` method is called, which accepts the arguments defined for the current `Paginator`. And this method returns a ready-made `JSON`.

Paginator consists of three methods: `.get_paginate_data()`, `.get_objects_data()`, `.paginate()`

### `.get_paginate_data()`
**Abstract Method**
This method adds information about the pagination itself. Must return a dictionary with data.


**Signature:** `.get_paginate_data(*args, **kwargs) -> dict`

* `args, kwargs` - Your custom data for pagination.

### `.get_objects_data()`
**Abstract Method**
This method adds information on the objects themselves from the list. Must return a dictionary with data.

**Signature:** `.get_objects_data() -> dict`

### `.paginate()`

This method generates complete JSON with data. Takes the same arguments as `.get_paginate_data()` and sends them to it.  Must return a dictionary with data.

**Signature:** `.paginate() -> dict`

---

## LimitOffsetResultPaginator

Paginator with `limit`,` offset`, `count`, `result` parameters.

**Example:**
```python
from rest_framework.views.paginations import LimitOffsetResultPaginator
all_objects = list(range(100))
current_page = all_objects[:10]

result = LimitOffsetResultPaginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'result': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

---

## LimitOffsetObjectsPaginator

Paginator with `limit`,` offset`, `count`, `objects` parameters.

**Example:**
```python
from rest_framework.views.paginations import LimitOffsetObjectsPaginator
all_objects = list(range(100))
current_page = all_objects[:10]

result = LimitOffsetObjectsPaginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'objects': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

---

## LimitOffsetItemsPaginator

Paginator with `limit`,` offset`, `count`, `items` parameters.

**Example:**
```python
from rest_framework.views.paginations import LimitOffsetItemsPaginator
all_objects = list(range(100))
current_page = all_objects[:10]

result = LimitOffsetItemsPaginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'items': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

---

# Paginator Mixins

`Mixins` for create `Paginators`.

## LimitOffsetGetPaginateDataMixin

Mixin for added to result JSON `limit`, `offset`, `count` fields.

**Example:**
```python
from rest_framework.views.paginations import BasePaginatorAbstract, LimitOffsetGetPaginateDataMixin

class Paginator(BasePaginatorAbstract, LimitOffsetGetPaginateDataMixin):
    def get_objects_data(self):
        return {'paginator': self.objects}

all_objects = list(range(100))
current_page = all_objects[:10]

result = Paginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'paginator': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

## ResultGetObjectsDataPaginatorMixin

Mixin for added to result JSON `result` fields.

**Example:**
```python
from rest_framework.views.paginations import BasePaginatorAbstract, ResultGetObjectsDataPaginatorMixin

class Paginator(BasePaginatorAbstract, ResultGetObjectsDataPaginatorMixin):
    def get_paginate_data(self, limit=10, offset=0, count=None):
        return dict(limit=limit, offset=offset, count=count)

all_objects = list(range(100))
current_page = all_objects[:10]

result = Paginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'result': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

## ObjectsGetObjectsDataPaginatorMixin

Mixin for added to result JSON `objects` fields.

**Example:**
```python
from rest_framework.views.paginations import BasePaginatorAbstract, ObjectsGetObjectsDataPaginatorMixin

class Paginator(BasePaginatorAbstract, ObjectsGetObjectsDataPaginatorMixin):
    def get_paginate_data(self, limit=10, offset=0, count=None):
        return dict(limit=limit, offset=offset, count=count)

all_objects = list(range(100))
current_page = all_objects[:10]

result = Paginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'objects': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

## ItemsGetObjectsDataPaginatorMixin

Mixin for added to result JSON `items` fields.

**Example:**
```python
from rest_framework.views.paginations import BasePaginatorAbstract, ItemsGetObjectsDataPaginatorMixin

class Paginator(BasePaginatorAbstract, ItemsGetObjectsDataPaginatorMixin):
    def get_paginate_data(self, limit=10, offset=0, count=None):
        return dict(limit=limit, offset=offset, count=count)

all_objects = list(range(100))
current_page = all_objects[:10]

result = Paginator(all_objects).paginate(limit=10, offset=0, count=100)
print(result)
# {'limit': 10, 'offset': 0, 'count': 100, 'items': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}
```

# Writing custom Paginator

Inherit the `rest_framework.views.paginations.BasePaginatorAbstract` class and define the methods: `.get_paginate_data(*args,**kwargs)`,`.get_objects_data()`. 
The very slice of objects is in `self.objects`.

**Example:**
```python
from rest_framework.views.paginations import BasePaginatorAbstract

class MyPaginator(BasePaginatorAbstract):
    def get_paginate_data(self, after=0, before=10, total=10):
        return dict(after=after, total=total)
    def get_objects_data(self):
        return dict(object=self.objects)

all_objects = list(range(100))
current_page = all_objects[:10]

result = MyPaginator(all_objects).paginate(after=10, total=10)
print(result)
# {'after': 10, 'total': 10, 'objects': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]}

```


[GetResponseMixin]: /api-guid/views/mixins#getresponsemixin