# Release Notes

## Versioning

Minor version numbers (0.0.x) are used for changes that are API compatible.  You should be able to upgrade between minor point releases without any other code changes.

Medium version numbers (0.x.0) may include API changes, in line with the [deprecation policy][deprecation-policy].  You should read the release notes carefully before upgrading between medium point releases.

Major version numbers (x.0.0) are reserved for substantial project milestones.

### 0.2.1

**Date:** [22th May 2019]

* Mini fix processing data in [`Serializers`][Serializers] `_field_validation` method.

### 0.2.0

**Date:** [3th April 2019]

* Mini fix [`Serializers`][Serializers] `_field_validation` method.
* Add [`BooleanNullField`][BooleanNullField].
* Remove Null values from [`BooleanField`][BooleanField].

### 0.1.9

**Date:** [23th March 2019]

* Fix incorrect 0.1.8 VERSION

### 0.1.8

**Date:** [23th March 2019]

* Mini fix [`SerializerMethodField`][SerializerMethodField] run `to_representation` method.

### 0.1.7

**Date:** [1st of January 2019]

* Added `__deepcopy__` method on all serializer fields.

### 0.1.6

**Date**: [18th December 2018].

* Fix internal logic on validation field binding.
* Fix settings internal validators on fields.

### 0.1.5

**Date**: [12th December 2018].

* Add [`RegexValidator`][RegexValidator].
* Add [`Inherit Serializers`][InheritSerializers].
* Add `six.iteritems` in all code.
* Fix mini bugs.

### 0.1.4

**Date**: [25th October 2018].

* Add [`JsonField`][JsonField], [`DictField`][DictField].
* Add [`SerializerMethodField`][SerializerMethodField].

### 0.1.3

**Date**: [17th October 2018].

* Add [`DateField`][DateField], [`TimeField`][TimeField], [`DateTimeField`][DateTimeField].
* Translate full project to english.
* `child` on [`ListField`][ListField] not required by default.

### 0.1.2

**Date**: [10th October 2018].

* Init serializers, fields, validators, docs, tests.
* Push to Open Source community.


[DateField]: api-guid/fields.md#-datefield
[BooleanNullField]: api-guid/fields.md#-booleannullfield
[BooleanField]: api-guid/fields.md#-booleanfield
[TimeField]: api-guid/fields.md#-timefield
[DateTimeField]: api-guid/fields.md#-datetimefield
[ListField]: api-guid/fields.md#-listfield
[JsonField]: api-guid/fields.md#-jsonfield
[DictField]: api-guid/fields.md#-dictfield
[SerializerMethodField]: api-guid/fields.md#-serializermethodfield
[InheritSerializers]: api-guid/serializers.md#serializer-inheritance
[RegexValidator]: api-guid/validators.md#regexvalidator
[Serializers]: api-guid/serializers.md
