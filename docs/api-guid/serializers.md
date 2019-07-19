# Serializers

Serializers allow complex data such as querysets and model instances to be converted to native Python datatypes that can then be easily rendered into `JSON`, `XML` or other content types.  Serializers also provide deserialization, allowing parsed data to be converted back into complex types, after first validating the incoming data.

## Declaring Serializers

Let's start by creating a simple object we can use for example:
```python
from datetime import datetime

class Comment(object):
    def __init__(self, author_name, content, created=False):
        self.author_name = author_name
        self.content = content
        self.created = bool(created)

comment = Comment(author_name='example_name', content='foo bar')
```
We'll declare a serializer that we can use to serialize and deserialize data that corresponds to `Comment` objects.
```python
from rest_framework import serializers

class CommentSerializer(serializers.Serializer):
    author_name = serializers.CharField(required=True)
    content = serializers.CharField(max_length=200)
    created = serializers.BooleanField(required=True)
```
---

## Serializing objects

We can now use `CommentSerializer` to serialize a comment, or list of comments.
```python
serializer = CommentSerializer(comment)
serializer.data
# {'author_name': 'example_name', 'content': 'foo bar', 'created': False}
```
---

## Deserializing objects

We restore those native datatypes into a dictionary of validated data.
```python
serializer = CommentSerializer(data=data)
serializer.is_valid()
# True
serializer.validated_data
# {'content': 'foo bar', 'author_name': 'example', 'created': False)}
```
With the same ease, you can deserialize several objects. You just need to add the `many=True` flag to the serializer constructor.
```python
serializer = CommentSerializer(data=[data, data], many=True)
serializer.is_valid()
# True
serializer.validated_data
# [
#   {'content': 'foo bar', 'author_name': 'example', 'created': False)}, 
#   {'content': 'foo bar', 'author_name': 'example', 'created': False)}
# ]
```
---

## Validation

When deserializing data, you always need to call `is_valid()` before attempting to access the validated data. If any validation errors occur, the `.errors` property will contain a dictionary representing the resulting error messages.  For example:
```python
serializer = CommentSerializer(data={'author_name': 'foobar', 'content': 'baz'})
serializer.is_valid()
# False
serializer.errors
# {'created': ['This field is required.']}
```
Each key in the dictionary will be the field name, and the values will be lists of strings of any error messages corresponding to that field.  The `non_field_errors` key may also be present, and will list any general validation errors.

When deserializing a list of items, errors will be returned as a list of dictionaries representing each of the deserialized items.

### Raising an exception on invalid data

The `.is_valid()` method takes an optional `raise_exception` flag that will cause it to raise a `serializers.ValidationError` exception if there are validation errors.
```python
serializer = CommentSerializer(data={'author_name': 'foobar', 'content': 'baz'})
try:
    serializer.is_valid(raise_exception=True)
except ValidationError:
    print(serializer.errors)
# {'created': ['This field is required.']}
```
---

### Field-level validation

You can specify custom field-level validation by adding `.validate_<field_name>` methods to your `Serializer` subclass.

These methods take a single argument, which is the field value that requires validation.

Your `validate_<field_name>` methods should return the validated value or raise a `serializers.ValidationError`.  For example:
```python
from rest_framework import serializers

class BlogPostSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    content = serializers.CharField()

    def validate_title(self, value):
        """
        Check that the blog post is about Django.

        """
        if 'rest' not in value.lower():
            raise serializers.ValidationError("Blog post is not about Rest")
        return value
```
---

### Object-level validation

To do any other validation that requires access to multiple fields, add a method called `.validate()` to your `Serializer` subclass.  This method takes a single argument, which is a dictionary of field values.  It should raise a `serializers.ValidationError` if necessary, or just return the validated values.  For example:
```python
from rest_framework import serializers

class EventSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=100)
    start = serializers.IntegerField()
    finish = serializers.IntegerField()

    def validate(self, data):
        """
        Check that the start is before the stop.

        """
        if data['start'] > data['finish']:
            raise serializers.ValidationError("finish must occur after start")
        return data
```
---

### Validators

Individual fields on a serializer can include validators, by declaring them on the field instance, for example:
```python
def multiple_of_ten(value):
    if value % 10 != 0:
        raise serializers.ValidationError('Not a multiple of ten')

class GameRecord(serializers.Serializer):
    score = IntegerField(validators=[multiple_of_ten])
    # ...
```
For more information see the [validators documentation](validators.md).

---

## Accessing the initial data and instance

When passing an initial object or queryset to a serializer instance, the object will be made available as `.instance`. If no initial object is passed then the `.instance` attribute will be `None`.

When passing data to a serializer instance, the unmodified data will be made available as `.initial_data`. If the data keyword argument is not passed then the `.initial_data` attribute will not exist.

---

## Dealing with nested objects

The previous examples are fine for dealing with objects that only have simple datatypes, but sometimes we also need to be able to represent more complex objects, where some of the attributes of an object might not be simple datatypes such as strings, dates or integers.

The `Serializer` class is itself a type of `Field`, and can be used to represent relationships where one object type is nested inside another.
```python
class UserSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    username = serializers.CharField(max_length=100)

class CommentSerializer(serializers.Serializer):
    user = UserSerializer()
    content = serializers.CharField(max_length=200)
```
If a nested representation may optionally accept the `None` value you should pass the `required=False` flag to the nested serializer.
```python
class CommentSerializer(serializers.Serializer):
    user = UserSerializer(required=False)  # May be an anonymous user.
    content = serializers.CharField(max_length=200)
```
Similarly if a nested representation should be a list of items, you should pass the `many=True` flag to the nested serialized.
```python
class CommentSerializer(serializers.Serializer):
    user = UserSerializer(required=False)
    edits = UserSerializer(many=True)  # A nested list of 'user' items.
    content = serializers.CharField(max_length=200)
```
---

## Writable nested representations

When dealing with nested representations that support deserializing the data, any errors with nested objects will be nested under the field name of the nested object.
```python
serializer = CommentSerializer(data={'user': {'username': 'doe'}, 'content': 'baz'})
serializer.is_valid()
# False
serializer.errors
# {'user': {'email': [u'Enter a valid e-mail address.']}}
```
Similarly, the `.validated_data` property will include nested data structures.

---

# BaseSerializer

`BaseSerializer` class that can be used to easily support alternative serialization and deserialization styles.

This class implements the same basic API as the `Serializer` class:

* `.data` - Returns the outgoing primitive representation.

There are five methods that can be overridden, depending on what functionality you want the serializer class to support:

* `.to_representation()` - Override this to support serialization, for read operations.
* `.to_internal_value()` - Override this to support deserialization, for write operations.
* `.is_valid()` - Deserializes and validates incoming data.
* `.validated_data` - Returns the validated incoming data.
* `.errors` - Returns any errors during validation.

Because this class provides the same interface as the `Serializer` class, you can use it with the existing generic class-based views exactly as you would for a regular `Serializer`.

---

# Advanced serializer usage

## Overriding serialization and deserialization behavior

If you need to alter the serialization or deserialization behavior of a serializer class, you can do so by overriding the `.to_representation()` or `.to_internal_value()` methods.

Some reasons this might be useful include...

* Adding new behavior for new serializer base classes.
* Modifying the behavior slightly for an existing class.
* Improving serialization performance for a frequently accessed API endpoint that returns lots of data.

The signatures for these methods are as follows:

---


### `.to_representation(self, instance)`

Takes the object instance that requires serialization, and should return a primitive representation. Typically this means returning a structure of built-in Python datatypes. The exact types that can be handled will depend on the render classes you have configured for your API.

May be overridden in order modify the representation style. For example:
```python
def to_representation(self, instance):
    """Convert `username` to lowercase."""
    ret = super().to_representation(instance)
    ret['username'] = ret['username'].lower()
    return ret
```
---

### `.to_internal_value(self, data)`

Takes the unvalidated incoming data as input and should return the validated data that will be made available as `serializer.validated_data`.

If any of the validation fails, then the method should raise a `serializers.ValidationError(errors)`. The `errors` argument should be a dictionary mapping field names (or `non_field_errors`) to a list of error messages. If you don't need to alter deserialization behavior and instead want to provide object-level validation, it's recommended that you instead override the [`.validate()`](#object-level-validation) method.

The `data` argument passed to this method will normally be the value of `request.data`, so the datatype it provides will depend on the parser classes you have configured for your API.

---

## Serializer Inheritance

You can extend and reuse serializers through inheritance. This allows you to declare a common set of fields or methods on a parent class that can then be used in a number of serializers. For example,
```python
class MyBaseSerializer(Serializer):
    my_field = serializers.CharField()

    def validate_my_field(self, value):
        ...

class MySerializer(MyBaseSerializer):
    ...
```
It’s possible to declaratively remove a `Field` inherited from a parent class by setting the name to be `None` on the subclass.
```python
class MyBaseSerializer(ModelSerializer):
    my_field = serializers.CharField()

class MySerializer(MyBaseSerializer):
    my_field = None
```
## Dynamically modifying fields

Once a serializer has been initialized, the dictionary of fields that are set on the serializer may be accessed using the `.fields` attribute.  Accessing and modifying this attribute allows you to dynamically modify the serializer.

Modifying the `fields` argument directly allows you to do interesting things such as changing the arguments on serializer fields at runtime, rather than at the point of declaring the serializer.

---
