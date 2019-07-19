<p class="badges">
    <a href="https://pypi.org/project/Python-Rest-Framework/">
        <img src="https://img.shields.io/pypi/v/python-rest-framework.svg" class="status-badge">
    </a>
    <a href="https://travis-ci.org/nxexox/python-rest-framework?branch=master">
        <img src="https://travis-ci.org/nxexox/python-rest-framework.svg?branch=master" class="status-badge">
    </a>
    <a href="https://codecov.io/gh/nxexox/python-rest-framework">
        <img src="https://codecov.io/gh/nxexox/python-rest-framework/branch/master/graph/badge.svg" class="status-badge">
    </a>
</p>

---

# [Python Rest Framework][repo]

Python Rest Framework is a full-fledged rest api engine.
You can concentrate all your strength on business logic, take care of the rest of the Python Rest Framework.

Full documentation for the project is available at [https://nxexox.github.io/python-rest-framework/][docs].

## Requirements

* Python (3.4, 3.5, 3.6, 3.7)
* six

## Installation

Install using `pip`, including any optional packages you want...
```bash
pip install python-rest-framework
```
...or clone the project from github.
```bash
git clone git@github.com:nxexox/python-rest-framework.git
```

## Versions for Python Web Frameworks

```bash
pip install python-rest-framework[flask]  # For Flask framework
pip install python-rest-framework[aiohttp]  # For AioHttp framework
pip install python-rest-framework[sanic]  # For Sanic framework
```

## Example

For example, we will serialize the data from the request object.

First we write the serializer
```python
from rest_framework.serializers import (
    Serializer, CharField, IntegerField, ListField, FloatField
)

# Example serializer for parsing body data from web request.
class ExampleSerializer(Serializer):
    char_field = CharField(label='This char field', required=True)
    int_field = IntegerField(label='This int field', required=True)
    list_float_field = ListField(child=FloatField(), required=True, min_length=2)
```

---

Now we process the request body with a serializer
```python
# web request data
data = {
    'char_field': 'example', 'int_field': 1,
    'list_float_field': [1.0, 1.1, 1.2]
}

ser = ExampleSerializer(data=data)
if ser.is_valid():
    print(ser.validated_data)
else:
    print(ser.errors)
```

[repo]: https://github.com/nxexox/python-rest-framework/
