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

## MinLengthValidator

This validator checks for greater than or equal to the minimum length of the object being iterated.

**Signature**: `MinLengthValidator(min_length, message=None)`

- `min_length` Minimal length for value.
- `message` The short message should fall out on validation error.

## MaxLengthValidator

This validator checks for less than or equal to the maximum length of the object to be iterated.

**Signature**: `MaxLengthValidator(max_length, message=None)`

- `max_length` Maximum length for value.
- `message` The short message should fall out on validation error.

## MinValueValidator

This validator checks for greater than or equal to the minimum value.

**Signature**: `MinValueValidator(min_value, message=None)`

- `min_value` Minimal valid value.
- `message` The short message should fall out on validation error.

## MaxValueValidator

This validator checks for less than or equal to the maximum value.

**Signature**: `MaxValueValidator(max_value, message=None)`

- `max_value` Maximal valid value.
- `message` The short message should fall out on validation error.

---

# Writing custom validators

You can write your own custom validators.

## Function based

A validator may be any callable that raises a `serializers.ValidationError` on failure.

    def even_number(value):
        if value % 2 != 0:
            raise serializers.ValidationError('This field must be an even number.')

#### Field-level validation

You can specify custom field-level validation by adding `.validate_<field_name>` methods
to your `Serializer` subclass.

## Class-based

To write a class-based validator, use the `__call__` method. Class-based validators are useful as they allow you to parameterize and reuse behavior.

    class MultipleOf(object):
        def __init__(self, base):
            self.base = base

        def __call__(self, value):
            if value % self.base != 0:
                message = 'This field must be a multiple of %d.' % self.base
                raise serializers.ValidationError(message)
