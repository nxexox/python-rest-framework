# Validators

Most of the time you're dealing with validation in REST framework you'll simply be relying on the default field validation, or writing explicit validation methods on serializer or field classes.

However, sometimes you'll want to place your validation logic into reusable components, so that it can easily be reused throughout your codebase. This can be achieved by using validator functions and validator classes.

---

## BaseValidator

This is the base class for validators. You can inherit from it, or write your own.

**Signature**: `BaseValidator(message=None)`

- `message` The short message should fall out on validation error.

You need to define the method __call__.

**Signature** `__call__(self, value)`

- `value` Value to validate.

## RequiredValidator

This is a validator to check for required fields. Checks value using None.

**Signature**: `RequiredValidator(message=None)`

- `message` The short message should fall out on validation error.

**Example**:
```python
validator = RequiredValidator()
validator('Not empty string')

try:
    validator(None)
except ValidationError:
    pass
```
## MinLengthValidator

This validator checks for greater than or equal to the minimum length of the object being iterated.

**Signature**: `MinLengthValidator(min_length, message=None)`

- `min_length` Minimal length for value.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = MinLengthValidator(10)
validator(list(range(15))

try:
    validator(list(range(9)))
except ValidationError:
    pass
```
## MaxLengthValidator

This validator checks for less than or equal to the maximum length of the object to be iterated.

**Signature**: `MaxLengthValidator(max_length, message=None)`

- `max_length` Maximum length for value.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = MaxLengthValidator(10)
validator(list(range(9))

try:
    validator(list(range(15)))
except ValidationError:
    pass
```
## MinValueValidator

This validator checks for greater than or equal to the minimum value.

**Signature**: `MinValueValidator(min_value, message=None)`

- `min_value` Minimal valid value.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = MinValueValidator(10)
validator(15)

try:
    validator(9)
except ValidationError:
    pass
```
## MaxValueValidator

This validator checks for less than or equal to the maximum value.

**Signature**: `MaxValueValidator(max_value, message=None)`

- `max_value` Maximal valid value.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = MaxValueValidator(10)
validator(9)

try:
    validator(15)
except ValidationError:
    pass
```
## RegexValidator

This validator checks the string against a regular expression.

**Signature**: `RegexValidator(regex, inverse_match=None, flags=None, message=None)`

- `regex` Regex raw
- `inverse_match` - A flag indicating whether to invert the response? Default: `False`.
- `flags` - Flags for compiling regular expression. Default `0`.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = RegexValidator(r'\d+')
validator('123')

try:
    validator('example')
except ValidationError:
    pass

validator = RegexValidator(r'\d+', True)
validator('test')
```
## ChoiceValidator

This validator checks a value for an entry in a predefined list of values.

**Signature**: `ChoiceValidator(choices, message=None)`

- `choices` Valid values. Iter object. If `list`, `tuple`, `set` check into iter object. If `dict`, check key.
- `message` The short message should fall out on validation error.

**Example**:
```python
validator = ChoiceValidator([1, 2, 3])
validator(2)

try:
    validator(15)
except ValidationError:
    pass
```
---

# Writing custom validators

You can write your own custom validators.

## Function based

A validator may be any callable that raises a `serializers.ValidationError` on failure.
```python
def even_number(value):
    if value % 2 != 0:
        raise serializers.ValidationError('This field must be an even number.')
```
#### Field-level validation

You can specify custom field-level validation by adding `.validate_<field_name>` methods
to your `Serializer` subclass. Read more [`Field Level Validation`][FieldLevelValidation]

## Class-based

To write a class-based validator, use the `__call__` method. Class-based validators are useful as they allow you to parameterize and reuse behavior.
```python
class MultipleOf(object):
    def __init__(self, base):
        self.base = base

    def __call__(self, value):
        if value % self.base != 0:
            message = 'This field must be a multiple of %d.' % self.base
            raise serializers.ValidationError(message)
```

[FieldLevelValidation]: /serializers#field-level-validation
