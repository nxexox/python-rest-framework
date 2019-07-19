# Sanic Views

`Sanic` has two `BaseClassViews`: `HTTPMethodView`, `CompositionView`. `Python-Rest-Framework` is connected to both.

**Note:** To use `SanicViews` you need to install `sanic`.

**All Classes can be found here:**
```python
from rest_framework.views.sanic import *
```

---

# SanicBaseViews

---

## SanicApiMethodView
This class is a successor: `sanic.views.HTTPMethodView`,` rest_framework.views.BaseApiView`.

What the class consists of:

* The class is completely safe. The class does not completely change the source code of Flask, and does not restrict from the source functions of the framework.
* Class implemented properties: `request_object`,` current_request_method`.
* Using the `rest_framework.views.BaseApiView._dispatch` method is configured and can be adjusted by setting the `use_dispatch`. By default `use_dispatch` set in `True`.
* For current work, added `self._request` attribute.
* The class itself uses `response_class=json_response`:
```python
from sanic import response

json_response = response.json
```

**Example:**
```python
from rest_framework.views.sanic import SanicApiMethodView


class MyView(SanicApiMethodView):
    def get(self, request, *args, **kwargs):
        # your view code
```

---

## SanicApiCompositionView
This class is a successor: `sanic.views.SanicApiCompositionView`,` rest_framework.views.BaseApiView`.

What the class consists of:

* The class is completely safe. The class does not completely change the source code of Flask, and does not restrict from the source functions of the framework.
* Class implemented properties: `request_object`,` current_request_method`.
* Using the `rest_framework.views.BaseApiView._dispatch` method is configured and can be adjusted by setting the `use_dispatch`. By default `use_dispatch` set in `True`.
* For current work, added `self._request` attribute.
* The class itself uses `response_class=json_response`:
```python
from sanic import response

json_response = response.json
```

**Example:**
```python
from sanic.response import text
from rest_framework.views.sanic import SanicApiCompositionView

class MyCompositionView(SanicApiCompositionView):
    def get_handler(self, request):
        return text('I am a get method')

view = MyCompositionView()
view.add(['GET'], view.get_handler)
```

---

# Sanic Mixins

Mixins for `Sanic` ​​are the same useful mixins as `rest_framework.views.mixins`, but they can only be used in `Sanic`.

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
from rest_framework.views.sanic import SanicApiMethodView, GetValidJsonMixin

class MyView(SanicApiMethodView, GetValidJsonMixin):
    serializer_classes = {
        'get': MySerializer()
    }
    def get(self, request, *args, **kwargs):
        request_data = self.get_valid_json()

#############
### Equivalent to
#############

from rest_framework.views.sanic import SanicApiMethodView
from rest_framework.views.mixins import GetSerializerMixin

class MyView(SanicApiMethodView, GetSerializerMixin):
    def get(self, request, *args, **kwargs):
        serializer_class = self.get_request_serializer()
        try:
            data = self.request_object.json
        except Exception:
            data = {}
        ser = serializer_class(data=data)
        ser.is_valid(raise_exception=True)
        request_data = ser.validated_data

```

---

# SanicGenericViews

`GenericViews` are ready-to-use classes, compiled from base classes and mixins for various needs.

---

## GetSerializerApiGenericMethodView

Generic Api method view for `GetSerializer` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiMethodView`
* `rest_framework.views.mixins.GetSerializer`

---

## GetResponseApiGenericMethodView

Generic Api method view for `GetResponse` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiMethodView`
* `rest_framework.views.mixins.GetResponse`

---

## GetValidJsonApiGenericMethodView

Generic Api method view for `GetValidJson` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiMethodView`
* `rest_framework.views.sanic.mixins.GetValidJson`

---

## ApiGenericMethodView
Generic Api method view for all mixins methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiMethodView`
* `rest_framework.views.sanic.mixins.GetValidJson`
* `rest_framework.views.mixins.GetSerializer`
* `rest_framework.views.mixins.GetResponse`

---


## GetSerializerApiGenericCompositionView

Generic Api composition view for `GetSerializer` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiCompositionView`
* `rest_framework.views.mixins.GetSerializer`

---

## GetResponseApiGenericCompositionView

Generic Api composition view for `GetResponse` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiCompositionView`
* `rest_framework.views.mixins.GetResponse`

---

## GetValidJsonApiGenericCompositionView

Generic Api composition view for `GetValidJson` methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiCompositionView`
* `rest_framework.views.sanic.mixins.GetValidJson`

---

## ApiGenericCompositionView

Generic Api composition view for all mixins methods.

**Parents:** 

* `rest_framework.views.sanic.SanicApiCompositionView`
* `rest_framework.views.sanic.mixins.GetValidJson`
* `rest_framework.views.mixins.GetSerializer`
* `rest_framework.views.mixins.GetResponse`

---

[GetSerializerMixin]: /api-guid/views/mixins#getserializermixin
