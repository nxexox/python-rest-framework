# Flask Views

`Flask` has two `BaseClassViews`: `View`, `MethodView`. `Python-Rest-Framework` is connected to both.

**Note:** To use `FlaskViews` you need to install `Flask`.

**All Classes can be found here:**
```python
from rest_framework.views.flask import *
```

---

# FlaskBaseViews

---

## FlaskBaseApiView
This class is a successor: `flask.views.View`,` rest_framework.views.BaseApiView`.

What the class consists of:

* The class is completely safe. The class does not completely change the source code of Flask, and does not restrict from the source functions of the framework.
* Class implemented properties: `request_object`,` current_request_method`.
* Using the `rest_framework.views.BaseApiView._dispatch` method is configured and can be adjusted by setting the `use_dispatch`. By default `use_dispatch` set in `True`.
* The class itself uses `response_class=json_response`:
```python
from flask import jsonify, make_response

def json_response(data, status=200, content_type='application/json'):
    return make_response(jsonify(data), status, content_type=content_type)
```

**Example:**
```python
from rest_framework.views.flask import FlaskBaseApiView


class MyView(FlaskBaseApiView):
    def dispatch_request(self, *args, **kwargs):
        # your view code
```

---

## FlaskBaseMethodView
This class is a successor: `flask.views.MethodView`,` rest_framework.views.BaseApiView`.

What the class consists of:

* The class is completely safe. The class does not completely change the source code of Flask, and does not restrict from the source functions of the framework.
* Class implemented properties: `request_object`,` current_request_method`.
* Using the `rest_framework.views.BaseApiView._dispatch` method is configured and can be adjusted by setting the `use_dispatch`. By default `use_dispatch` set in `True`.
* The class itself uses `response_class=json_response`:
```python
from flask import jsonify, make_response

def json_response(data, status=200, content_type='application/json'):
    return make_response(jsonify(data), status, content_type=content_type)
```

**Example:**
```python
from rest_framework.views.flask import FlaskBaseMethodView


class MyView(FlaskBaseMethodView):
    def get(self):
        # your view code
```

---

# Flask Mixins

Mixins for `Flask` ​​are the same useful mixins as `rest_framework.views.mixins`, but they can only be used in `Flask`.

---

## GetValidJsonMixin
The class is successor: `rest_framework.views.GetSerializerMixin`

Mixin adds the `.get_valid_json()` method, which parses the query and body of the query, merges them, and automatically serializes it and validates it with `rest_framework.serializers.Serializer`.
You can describe the serializers themselves in the [`serializers_classes`][GetSerializerMixin] class attribute.

### `.get_valid_json()`

This method retrieves from the request all the data that the user sent. Serializes and validates them and returns as a dictionary.

**Signature:** `.get_valid_json(parse_query=False, raise_exception=True) -> dict`

* `parse_query(bool)` - Parse query params?
* `raise_exception(bool)` - Raise exception `ValidationError`, if validation error.

**Example:**
```python
from rest_framework.views.flask import FlaskBaseMethodView, GetValidJsonMixin

class MyView(FlaskBaseMethodView, GetValidJsonMixin):
    serializer_classes = {
        'get': MySerializer()
    }
    def get(self):
        request_data = self.get_valid_json()

#############
### Equivalent to
#############

from rest_framework.views.flask import FlaskBaseMethodView
from rest_framework.views.mixins import GetSerializerMixin

class MyView(FlaskBaseMethodView, GetSerializerMixin):
    def get(self):
        serializer_class = self.get_request_serializer()
        try:
            data = self.request_object.get_json()
        except Exception:
            data = {}
        ser = serializer_class(data=data)
        ser.is_valid(raise_exception=True)
        request_data = ser.validated_data

```

---

# FlaskGenericViews

`GenericViews` are ready-to-use classes, compiled from base classes and mixins for various needs.

---

## GetSerializerApiGenericView

Generic Api view for `GetSerializer` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseApiView`
* `rest_framework.views.mixins.GetSerializer`

---

## GetResponseApiGenericView

Generic Api view for `GetResponse` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseApiView`
* `rest_framework.views.mixins.GetResponse`

---

## GetValidJsonApiGenericView

Generic Api view for `GetValidJson` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseApiView`
* `rest_framework.views.flask.mixins.GetValidJson`

---

## ApiGenericView

Generic Api view for all mixins methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseApiView`
* `rest_framework.views.flask.mixins.GetValidJson`
* `rest_framework.views.mixins.GetSerializer`
* `rest_framework.views.mixins.GetResponse`

---

## GetSerializerApiGenericMethodView

Generic Api method view for `GetSerializer` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseMethodView`
* `rest_framework.views.mixins.GetSerializer`

---

## GetResponseApiGenericMethodView

Generic Api method view for `GetResponse` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseMethodView`
* `rest_framework.views.mixins.GetResponse`

---

## GetValidJsonApiGenericMethodView

Generic Api method view for `GetValidJson` methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseMethodView`
* `rest_framework.views.flask.mixins.GetValidJson`

---

## ApiGenericMethodView
Generic Api method view for all mixins methods.

**Parents:** 

* `rest_framework.views.flask.FlaskBaseMethodView`
* `rest_framework.views.flask.mixins.GetValidJson`
* `rest_framework.views.mixins.GetSerializer`
* `rest_framework.views.mixins.GetResponse`

---

[GetSerializerMixin]: /api-guid/views/mixins#getserializermixin
