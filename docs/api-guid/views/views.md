# Views

`Pytthon-Rest-Framework` provides an `BaseApiView` class.

`BaseApiView` classes are different from regular `View` classes in the following ways:

* Any `ApiException` exceptions will be caught and mediated into appropriate responses. It can be customized.
* The `BaseApiView` class has a `fail` method that can return a valid `JSON Response` for you for an error.
* You configure which class `Response` will return.
* With `View Mixins` you can flexibly build the functionality you need for your `View`.

Using the `BaseApiView` class is pretty much the same as using a regular `View` class, as usual, the incoming request is dispatched to an appropriate handler method such as `.get()` or `.post()`. Additionally, a number of attributes may be set on the class that control various aspects of the `API policy`.

**For example:**
```python
from rest_framework.views import BaseApiView, GetSerializerMixin, GetResponseMixin
from your_application.serializers import RequestSerializer, ResponseSerializer
from your_web_framework.response import json_response_class

class ApiView(BaseApiView, YourFrameworkApiView, GetSerializerMixin, GetResponseMixin):
    response_class = json_response_class
    serializer_classes = {
        'get': {
            'in': RequestSerializer,
            'out': ResponseSerializer
        }
    }
    
    @property
    def request_object(self):
        return self.request
    
    @property
    def current_request_method(self):
        return self.request_object.method  # type: str
    
    def get(self):
        ser_class = self.get_request_serializer()  # From GetSerializerMixin
        ser = ser_class(data=self.request_object.json())
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        # ...
        # Your data work
        # ...
        # Return valid response object and serialized {'result': 'ok'} ResponseSerializer
        return self.get_response({'result': 'ok'})  # From GetResponseMixin
```

But even in this example, we had to write additional methods `request_object`,` current_request_method`. These are internal methods for `GetResponseMixin` to work correctly. `Python-Rest-Framework` took care of this, and wrote all the internal implementations for different frameworks. Consider the same thing with the help of `Flask`.

```python
from rest_framework.views.flask import FlaskBaseMethodView, GetValidJsonMixin
from your_application.serializers import RequestSerializer, ResponseSerializer


class ApiView(FlaskBaseMethodView, GetSerializerMixin, GetResponseMixin, GetValidJsonMixin):
    serializer_classes = {
        'get': {
            'in': RequestSerializer,
            'out': ResponseSerializer
        }
    }
    
    def get(self):
        # Auto get data.
        data = self.get_valid_json()  # From GetValidJsonMixin mixin
        # ...
        # Your data work
        # ...
        # Return valid response object and serialized {'result': 'ok'} ResponseSerializer
        return self.get_response({'result': 'ok'})  # From GetResponseMixin
```

Using the `BaseApiView` class directly is not recommended; instead, use the base classes for your framework or `GenericViews`.

## BaseApiView Attributes

These attributes allow you to customize the behavior of `BaseApiView`.

### `use_dispatch - bool` 
A flag that includes the base wrapper for all internal functions. Off by default. In all implementations for frameworks, the flag is on by default.

### `response_class - Callable`
Class `Response`. Default is None. Each framework has its own and is already installed and configured.

### `response_content_type - str`
Content response answer api. Used in methods that form `Response`, or raise errors `API`. Default: `application/json`.

---

## BaseApiView methods

### .fail()

Method that throws `ApiException`. To interrupt the processing of the request and give the client a `Response` with an error.

**Signature:** `fail(detail=None, status=400)`

* `detail` - `Dict` which will be returned to the client in `Response`.
* `status` - Server response status. The default is `400`. 

**Example:**

```python
from rest_framework.views.flask import FlaskBaseMethodView, GetValidJsonMixin
from your_application.serializers import RequestSerializer, ResponseSerializer

class ApiView(FlaskBaseMethodView, GetSerializerMixin, GetResponseMixin, GetValidJsonMixin):
    serializer_classes = {
        'get': {
            'in': RequestSerializer,
            'out': ResponseSerializer
        }
    }
    
    def get(self):
        # Auto get data.
        data = self.get_valid_json()  # From GetValidJsonMixin mixin
        # ...
        # Your data work
        # ...
        
        if data.get('not_exists_field', None) is None:
            self.fail('not_exists_field field is required')
        
        # Return valid response object and serialized {'result': 'ok'} ResponseSerializer
        return self.get_response({'result': 'ok'})  # From GetResponseMixin
```

--- 

# Writing custom FrameworkBaseView

You need to inherit from `rest_framework.views.BaseApiView` and do some work.

* Implement the properties `request_object`,` request_object_method`, so that you can use `Views Mixins`.
* Wrap your `view` into the` _dispatch` method.

###  `._dispatch()`

A method that adds its logic to `Views`.

**Signature:** `._dispatch(method, *args, **kwargs)`

* `method(Callable)` - User request handler.
* `args, kwargs` - Arguments for user request handler.

**Example(For Flask Framework):**
```python
from flask import request, jsonify, make_response
from flask.views import MethodView

from rest_framework.views.base import BaseApiView


def json_response(data, status=200, content_type='application/json'):
    return make_response(jsonify(data), status, content_type=content_type)


class FlaskBaseMethodView(MethodView, BaseApiView):
    response_class = json_response

    @property
    def request_object(self):
        return request

    @property
    def current_request_method(self):
        return request.method
    
    def dispatch_request(self, *args, **kwargs):
        meth = getattr(self, request.method.lower(), None)

        # If the request method is HEAD and we don't have a handler for it
        # retry with GET.
        if meth is None and request.method == 'HEAD':
            meth = getattr(self, 'get', None)

        assert meth is not None, 'Unimplemented method %r' % request.method
        
        # Wrapped in a method _dispatch
        if self.use_dispatch:
            return self._dispatch(meth, *args, **kwargs)
        return meth(*args, **kwargs)

```

---
