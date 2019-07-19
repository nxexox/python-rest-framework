# Views Mixins

`Pytthon-Rest-Framework` provides views mixins, for easy customization of your `API`.

`View Mixins` is a powerful `Python-Rest-Framework` tool, with which you can very flexibly configure only the functionality that you need.

Each mixin provides its own functionality and asks for its settings. `Views Mixins` do not overlap in functionality, so you can use any combination of them.

`Views Mixins` is not only common for all types of frameworks, but also specific for each framework.

**All Mixins can be found here:**
```python
from rest_framework.views.mixins import *
```

---

## Mixins

---

## GetRequestAbstractMixin

Basic mixin, which is an asbestos class and requires the implementation of:

* `request_object` - The class property that the query object returns. This property is used by all inherited mixins.
The property requires implementation. In the base classes for frameworks, this property is already implemented and you do not need to worry.

**Example(Flask):**
```python
from flask import request, jsonify, make_response
from flask.views import View
from rest_framework.views.mixins import GetRequestAbstractMixin


class MyView(View, GetRequestAbstractMixin):
    
    @property
    def request_object(self):
        return request
```

* `current_request_method` - A class property that returns the name of the current HTTP request method. `GET`,` POST` and `etc` ...
The property requires implementation. In the base class for frameworks, this property is already implemented and you do not need to worry.

**Example(Flask):**
```python
from flask import request, jsonify, make_response
from flask.views import View
from rest_framework.views.mixins import GetRequestAbstractMixin


class MyView(View, GetRequestAbstractMixin):
    
    @property
    def current_request_method(self):
        return request.method
```

---

## GetSerializerMixin

Mixin, which allows you to conveniently work with serializers.

Provides methods: `get_serializer`,` get_request_serializer`, `get_response_serializer`.
All these methods look for serializers in the class attribute `serializer_classes (Dict)` according to certain rules:

* At the first level of the dictionary, the name of the request method is `GET`,` POST` and etc:
```python
from rest_framework.views import GetSerializerMixin

class ExampleView(GetSerializerMixin):
    serializer_classes = {
        'get': None,
        'post': None
    }
```

---

**Note:** You must add the methods you want to use in your view.

---

* At the second level, there must be either a `Serializer` or another dictionary. The dictionary must consist of either one or two keys: `in`,` out`.

```python
from rest_framework.views import GetSerializerMixin

class ExampleView(GetSerializerMixin):
    serializer_classes = {
        'get': GetSerializer,
        'post': {
            'in': PostRequestSerializer
        },
        'put': {
            'in': PutRequestSerializer,
            'out': PutResponseSerializer
        }
    }
```

### `.get_request_serializer()`

A method that returns a `Serializer` to process data from a client.
```python
from rest_framework.views import GetSerializerMixin

class ExampleView(GetSerializerMixin):
    serializer_classes = {
        'get': GetSerializer,
        'post': {
            'in': PostRequestSerializer
        },
        'put': {
            'in': PutRequestSerializer,
            'out': PutResponseSerializer
        },
        'patch': {}
    }
    
    def get(self):
        ser = self.get_request_serializer()
        # ser - GetSerializer
    
    def post(self):
        ser = self.get_request_serializer()
        # ser - PostRequestSerializer
    
    def put(self):
        ser = self.get_request_serializer()
        # ser - PutRequestSerializer
    
    def patch(self):
        ser = self.get_request_serializer()
        # ser - None
    
    def delete(self):
        ser = self.get_request_serializer()
        # ser - None
```

### `.get_response_serializer()`

A method that returns a `Serializer` to serialize data to return to a user. For `Response`.
```python
from rest_framework.views import GetSerializerMixin

class ExampleView(GetSerializerMixin):
    serializer_classes = {
        'get': GetSerializer,
        'post': {
            'in': PostRequestSerializer
        },
        'put': {
            'in': PutRequestSerializer,
            'out': PutResponseSerializer
        },
        'patch': {}
    }
    
    def get(self):
        ser = self.get_response_serializer()
        # ser - GetSerializer
    
    def post(self):
        ser = self.get_response_serializer()
        # ser - None
    
    def put(self):
        ser = self.get_response_serializer()
        # ser - PutResponseSerializer
    
    def patch(self):
        ser = self.get_response_serializer()
        # ser - None
    
    def delete(self):
        ser = self.get_response_serializer()
        # ser - None
```

### `.get_serializer()`

Method for search `Serializer`.

**Signature:** `get_serializer(key: str)`

* `key(str)` - Key for search. `in` or `out`.

**Example:**
```python
from rest_framework.views import GetSerializerMixin

class ExampleView(GetSerializerMixin):
    serializer_classes = {
        'get': GetSerializer,
        'post': {
            'in': PostRequestSerializer
        },
        'put': {
            'in': PutRequestSerializer,
            'out': PutResponseSerializer
        },
        'patch': {}
    }
    
    def get(self):
        ser = self.get_serializer('in')
        # ser - GetSerializer
        ser = self.get_serializer('out')
        # ser - GetSerializer
    
    def post(self):
        ser = self.get_serializer('in')
        # ser - PostRequestSerializer
        ser = self.get_serializer('out')
        # ser - None
    
    def put(self):
        ser = self.get_serializer('in')
        # ser - PutRequestSerializer
        ser = self.get_serializer('out')
        # ser - PutResponseSerializer
    
    def patch(self):
        ser = self.get_serializer('in')
        # ser - None
        ser = self.get_serializer('out')
        # ser - None
    
    def delete(self):
        ser = self.get_serializer('in')
        # ser - None
        ser = self.get_serializer('out')
        # ser - None
```

---

## GetResponseMixin

Mixin for easy response to the client. 

**Attributes:**

* `response_class` - Response class, for create Response. Interface: data: Any(For JSON), status: int = response status, content_type: str = `application/json`
* `pagination_class` - Paginator class for get pagination json. Default: [`LimitOffsetObjectsPaginator`][LimitOffsetObjectsPaginator]. Read more in the section on [`pagination`][Paginations].
* `response_content_type` - Response Content Type, default: `application/json`

### `.get_response()`

Formation and preparation of response `Response object` for the client.

**Signature:** `.get_response(obj=None, is_serialized=True, status_code=200)`

* `obj(Any)` - Object for response body.
* `is_serialized(bool)` - Is data serialization required? Use `get_response_serializer()` for serilization result object? Default: `True`.
* `status_code(int)` - Code server response. Default: `200`.

**Example(AioHTTP):**
```python
from aiohttp.web import View, json_response
from rest_framework.views import GetResponseMixin

class ExampleView(View, GetResponseMixin):
    response_class = json_response
    serializer_classes = {
        'get': MyGetSerializer
    }
    
    async def get(self):
        # Your code
        data = MyModel()
        return self.get_response(data, is_serialized=True, status_code=200)
```

### `.get_list_response()`

Formation and preparation of response `Many Response objects` for the client.

**Signature:** `get_list_response(obj=None, is_serialized=True, status_code=200, *args, **kwargs)`

* `objs(List[Any])` - List Objects for response body.
* `is_serialized(bool)` - Is data serialization required? Use `get_response_serializer()` for serilization result object? Default: `True`.
* `status_code(int)` - Code server response. Default: `200`.
* `args, kwargs` - Arguments for pagination class. Read more in the section on [`pagination`][Paginations].

**Example(AioHTTP):**
```python
from aiohttp.web import View, json_response
from rest_framework.views import GetResponseMixin

class ExampleView(View, GetResponseMixin):
    response_class = json_response
    serializer_classes = {
        'get': MyGetSerializer
    }
    
    async def get(self):
        # Your code
        data = [MyModel(), MyModel(), MyModel()]
        return self.get_list_response(data, is_serialized=True, status_code=200)
```

---

# Writing custom FrameworkBaseView

To write your Mixin, you can inherit from `GetRequestAbstractMixin` if you need the properties` request_object`, `request_object_method`.
From any other `Mixin`, if you need its methods or attributes.
And from `object`, if your Mixin does not depend on the existing ones.

**Example:**
```python
class CustomHeadersMixin(object):
    def update_headers(self, headers):
        headers.update({'Custom-Auth-Header': 'HashCode'})
        return headers

```

[Paginations]: /api-giud/views/paginations
[LimitOffsetObjectsPaginator]: /api-guid/views/paginations#limitoffsetobjectspaginator
