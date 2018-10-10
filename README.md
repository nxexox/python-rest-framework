# Python Rest Framework

Python Rest Framework is a full-fledged rest api engine.
You can concentrate all your strength on business logic, take care of the rest of the Python Rest Framework.

## Requirements

* Python (3.4, 3.5, 3.6, 3.7)
* six

## Installation

Install using `pip`, including any optional packages you want...

    pip install python-rest-framework

...or clone the project from github.

    git clone git@github.com:nxexox/python-rest-framework.git


## Example

For example, we will serialize the data from the request object.

First we write the serializer

    from rest_framework.serializers import (
        Serializer, CharField, IntegerField, ListField, FloatField
    )

    # Example serializer for parsing body data from web request.
    class ExampleSerializer(Serializer):
        char_field = CharField(label='This char field', required=True)
        int_field = IntegerField(label='This int field', required=True)
        list_float_field = ListField(child=FloatField(), required=True, min_length=2)

---

Now we process the request body with a serializer

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
