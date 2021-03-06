# Fields

Serializer fields handle converting between primitive values and internal datatypes.  They also deal with validating input values, as well as retrieving and setting the values from their parent objects.

---

**Note:** The serializer fields are declared in `fields.py`, but by convention you should import them using `from rest_framework import serializers` and refer to fields as `serializers.<FieldName>`.

---

## Core arguments

Each serializer field class constructor takes at least these arguments.  Some Field classes take additional, field-specific arguments, but the following should always be accepted:

###`required`

Normally an error will be raised if a field is not supplied during deserialization.
Set to false if this field is not required to be present during deserialization.

Setting this to `False` also allows the object attribute or dictionary key to be omitted from output when serializing the instance. If the key is not present it will simply not be included in the output representation.

Defaults to `True`.

###`default`

If set, this gives the default value that will be used for the field if no input value is supplied. If not set the default behaviour is to not populate the attribute at all.

May be set to a function or other callable, in which case the value will be evaluated each time it is used. When called, it will receive no arguments.

When serializing the instance, default will be used if the the object attribute or dictionary key is not present in the instance.

Note that setting a `default` value implies that the field is not required. Enabling the arguments of the `default` keyword will set the` required` to `False`.

###`label`

A short text string that may be used as the name of the field in HTML form fields or other descriptive elements.

###`validators`

A list of validator functions which should be applied to the incoming field input, and which either raise a validation error or simply return. Validator functions should raise `serializers.ValidationError`.

###`error_messages`

A dictionary of error codes to error messages.

###`source`

The name of the field object with which the serializer field is associated. By default, the field name of the serializer = the name of the field of the object being serialized. This field changes this behavior.

**Example:**
```python
from rest_framework import serializers

class Model(object):
    field = 10

class StandardSerializer(serializers.Serializer):
    field = serializers.IntegerField()

class SourceFieldSerializer(serializers.Serializer):
    new_field = serializers.IntegerField(source='field')

print(StandardSerializer(instance=Model()).data)
# {'field': 10}
print(SourceFieldSerializer(instance=Model()).data)
# {'new_field': 10}
```

###`allow_none`

If set to True, skips None in the data field.

**Example:**
```python
from rest_framework import serializers

class StandardSerializer(serializers.Serializer):
    field = serializers.IntegerField()

class AllowNoneSerializer(serializers.Serializer):
    field = serializers.IntegerField(allow_none=True)

print(StandardSerializer(instance={'field': None}).data)
# Raise Validation Exception
print(AllowNoneSerializer(instance={'field': None}).data)
# {'field': None}
```

---

# Fields

## BooleanField

When using HTML encoded form input be aware that omitting a value will always be treated as setting a field to `False`, even if it has a `default=True` option specified. This is because HTML checkbox inputs represent the unchecked state by omitting the value, so REST framework treats omission as if it is an empty checkbox input.

**Signature:** `BooleanField()`

---

## BooleanNullField

A boolean representation that also accepts `None` as a valid value.

When using HTML encoded form input be aware that omitting a value will always be treated as setting a field to `False`, even if it has a `default=True` option specified. This is because HTML checkbox inputs represent the unchecked state by omitting the value, so REST framework treats omission as if it is an empty checkbox input.

**Signature:** `BooleanNullField()`

---

## CharField

A text representation. Optionally validates the text to be shorter than `max_length` and longer than `min_length`.

**Signature:** `CharField(max_length=None, min_length=None, trim_whitespace=True, allow_blank=False)`

- `min_length` - Validates that the input contains no fewer than this number of characters.
- `max_length` - Validates that the input contains no more than this number of characters.
- `allow_blank` - If set to `True` then the empty string should be considered a valid value. If set to `False` then the empty string is considered invalid and will raise a validation error. Defaults to `False`.
- `trim_whitespace` - If set to `True` then leading and trailing whitespace is trimmed. Defaults to `True`.

---

## IntegerField

An integer representation.

**Signature**: `IntegerField(min_value=None, max_value=None)`

- `min_value` Validate that the number provided is no less than this value.
- `max_value` Validate that the number provided is no greater than this value.

---

## FloatField

A floating point representation.

**Signature**: `FloatField(min_value=None, max_value=None)`

- `min_value` Validate that the number provided is no less than this value.
- `max_value` Validate that the number provided is no greater than this value.

---

# Date and time fields

## DateTimeField

A date and time representation.

**Signature:** `DateTimeField(format=None, input_format=None)`

* `format` - A string representing the output format. If not specified, this defaults to the same value as the `DEFAULT_DATETIME_FORMAT` settings key, which will be `'iso-8601'` unless set. Setting to a format string indicates that `to_representation` return values should be coerced to string output. Format strings are described below. Setting this value to `None` indicates that Python `datetime` objects should be returned by `to_representation`. In this case the datetime encoding will be determined by the renderer.
* `input_format` - String representing the input format which may be used to parse the date.  If not specified, the `DEFAULT_INPUT_DATETIME_FORMAT` setting will be used, which defaults to `'iso-8601'`.

#### `DateTimeField` format strings.

Format strings may either be [Python strftime formats][strftime] which explicitly specify the format, or the special string `'iso-8601'`, which indicates that [ISO 8601][iso8601] style datetimes should be used. (eg `'2013-01-29 12:34:56'`)

When a value of `None` is used for the format `datetime` objects will be returned by `to_representation` and the final output representation will determined by the renderer class.

## DateField

A date representation.

**Signature:** `DateField(format=None, input_format=None)`

* `format` - A string representing the output format.  If not specified, this defaults to the same value as the `DEFAULT_DATE_FORMAT` settings key, which will be `'iso-8601'` unless set. Setting to a format string indicates that `to_representation` return values should be coerced to string output. Format strings are described below. Setting this value to `None` indicates that Python `date` objects should be returned by `to_representation`. In this case the date encoding will be determined by the renderer.
* `input_format` - String representing the input format which may be used to parse the date.  If not specified, the `DEFAULT_INPUT_DATE_FORMATS` setting will be used, which defaults to `'iso-8601'`.

#### `DateField` format strings

Format strings may either be [Python strftime formats][strftime] which explicitly specify the format, or the special string `'iso-8601'`, which indicates that [ISO 8601][iso8601] style dates should be used. (eg `'2013-01-29'`)

## TimeField

A time representation.

**Signature:** `TimeField(format=None, input_format=None)`

* `format` - A string representing the output format.  If not specified, this defaults to the same value as the `DEFAULT_TIME_FORMAT` settings key, which will be `'iso-8601'` unless set. Setting to a format string indicates that `to_representation` return values should be coerced to string output. Format strings are described below. Setting this value to `None` indicates that Python `time` objects should be returned by `to_representation`. In this case the time encoding will be determined by the renderer.
* `input_format` - String representing the input format which may be used to parse the date.  If not specified, the `DEFAULT_INPUT_TIME_FORMATS` setting will be used, which defaults to `'iso-8601'`.

#### `TimeField` format strings

Format strings may either be [Python strftime formats][strftime] which explicitly specify the format, or the special string `'iso-8601'`, which indicates that [ISO 8601][iso8601] style times should be used. (eg `'12:34:56'`)

---

# Composite fields

## ListField

A field class that validates a list of objects.

**Signature**: `ListField(child=<A_FIELD_INSTANCE>, min_length=None, max_length=None, allow_empty=False)`

- `child` - A field instance that should be used for validating the objects in the list. If this argument is not provided then objects in the list will not be validated.
- `min_length` - Validates that the list contains no fewer than this number of elements.
- `max_length` - Validates that the list contains no more than this number of elements.
- `allow_blank` - If set to` True`, an empty array should be considered valid. If set to `False`, an empty array is considered invalid and causes a validation error. The default is `False`.

For example, to validate a list of integers you might use something like the following:
```python
scores = serializers.ListField(
   child=serializers.IntegerField(min_value=0, max_value=100)
)
```
The `ListField` class also supports a declarative style that allows you to write reusable list field classes.
```python
class StringListField(serializers.ListField):
    child = serializers.CharField()
```
We can now reuse our custom `StringListField` class throughout our application, without having to provide a `child` argument to it.

## JSONField

A field class that validates that the incoming data structure consists of valid JSON primitives. In its alternate binary mode, it will represent and validate JSON-encoded binary strings.

**Signature**: `JSONField()`

## DictField

A field class that validates a dictionary of objects. The keys in `DictField` are always assumed to be string values.

**Signature**: `DictField(child=<A_FIELD_INSTANCE>)`

- `child` - A field instance that should be used for validating the values in the dictionary. If this argument is not provided then values in the mapping will not be validated.

For example, to create a field that validates a mapping of strings to strings, you would write something like this:
```python
document = DictField(child=CharField())
```
You can also use the declarative style, as with `ListField`. For example:
```python
class DocumentField(DictField):
    child = CharField()
```
---

# Miscellaneous fields

## SerializerMethodField

It gets its value by calling a method on the serializer class it is attached to. It can be used to add any sort of data to the serialized representation of your object.

**Signature**: `SerializerMethodField(method_name_get=None, method_name_pop=None)`

- `method_name_get` - The name of the method on the calling serializer during object scrapping. If not included this defaults to `get_<field_name>`.
- `method_name_pop` - The name of the method on the calling serializer during validation data. If not included this defaults to `pop_<field_name>`.

The serializer method referred to by the `method_name_get` argument should accept a single argument (in addition to `self`), which is the object being serialized. It should return whatever you want to be included in the serialized representation of the object. For example:
```python
from datetime.datetime import now
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    days_since_joined = serializers.SerializerMethodField()

    def get_days_since_joined(self, obj):
        return (now() - obj.date_joined).days
```
The serializer method referenced by the `method_name_pop` argument must take one argument (in addition to` self`), which is the value to process and validate. It must return whatever you want to include in the validated view of the data. For example:
```python
from datetime.datetime import now
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    rgb = serializers.SerializerMethodField()

    def pop_rgb(self, data):
        return data.split(';')[1:3]
```
---

# Custom fields

If you want to create a custom field, you'll need to subclass `Field` and then override either one or both of the `.to_representation()` and `.to_internal_value()` methods.  These two methods are used to convert between the initial datatype, and a primitive, serializable datatype. Primitive datatypes will typically be any of a number, string, boolean, `date`/`time`/`datetime` or `None`. They may also be any list or dictionary like object that only contains other primitive objects. Other types might be supported, depending on the renderer that you are using.

The `.to_representation()` method is called to convert the initial datatype into a primitive, serializable datatype.

The `to_internal_value()` method is called to restore a primitive datatype into its internal python representation. This method should raise a `serializers.ValidationError` if the data is invalid.

---

## Examples

### A Basic Custom Field

Let's look at an example of serializing a class that represents an RGB color value:
```python
class Color(object):
    """
    A color represented in the RGB colorspace.

    """
    def __init__(self, red, green, blue):
        assert(red >= 0 and green >= 0 and blue >= 0)
        assert(red < 256 and green < 256 and blue < 256)
        self.red, self.green, self.blue = red, green, blue

class ColorField(serializers.Field):
    """
    Color objects are serialized into 'rgb(#, #, #)' notation.

    """
    def to_representation(self, value):
        return "rgb(%d, %d, %d)" % (value.red, value.green, value.blue)

    def to_internal_value(self, data):
        data = data.strip('rgb(').rstrip(')')
        red, green, blue = [int(col) for col in data.split(',')]
        return Color(red, green, blue)
```
By default field values are treated as mapping to an attribute on the object or key Mapping collection.  If you need to customize how the field value is accessed and set you need to override `.get_attribute()`.

As an example, let's create a field that can be used to represent the class name of the object being serialized:
```python
class ClassNameField(serializers.Field):
    def get_attribute(self, instance):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute.
        return instance

    def to_representation(self, value):
        """
        Serialize the value's class name.

        """
        return value.__class__.__name__
```
### Raising validation errors

Our `ColorField` class above currently does not perform any data validation.
To indicate invalid data, we should raise a `serializers.ValidationError` or call `self.fail_validate(detail, status=400)`, like so:
```python
def to_internal_value(self, data):
    if not isinstance(data, six.text_type):
        msg = 'Incorrect type. Expected a string, but got %s'
        raise ValidationError(detail=msg % type(data).__name__)

    if not re.match(r'^rgb\([0-9]+,[0-9]+,[0-9]+\)$', data):
        raise ValidationError(detail='Incorrect format. Expected `rgb(#,#,#)`.', status=500)

    data = data.strip('rgb(').rstrip(')')
    red, green, blue = [int(col) for col in data.split(',')]

    if any([col > 255 or col < 0 for col in (red, green, blue)]):
        self.fail_validate(detail='Value out of range. Must be between 0 and 255.')

    return Color(red, green, blue)
```
The `.fail_field_validation()` method is a shortcut for raising `ValidationError` that takes a message string from the `error_messages` dictionary. For example:
```python
default_error_messages = {
    'incorrect_type': 'Incorrect type. Expected a string, but got {input_type}',
    'incorrect_format': 'Incorrect format. Expected `rgb(#,#,#)`.',
    'out_of_range': 'Value out of range. Must be between 0 and 255.'
}

def to_internal_value(self, data):
    if not isinstance(data, six.text_type):
        self.fail_field_validation('incorrect_type', input_type=type(data).__name__)

    if not re.match(r'^rgb\([0-9]+,[0-9]+,[0-9]+\)$', data):
        self.fail_field_validation('incorrect_format')

    data = data.strip('rgb(').rstrip(')')
    red, green, blue = [int(col) for col in data.split(',')]

    if any([col > 255 or col < 0 for col in (red, green, blue)]):
        self.fail_field_validation('out_of_range')

    return Color(red, green, blue)
```
This style keeps your error messages cleaner and more separated from your code, and should be preferred.

[iso8601]: https://www.w3.org/TR/NOTE-datetime
