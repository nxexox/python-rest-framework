# Release Notes

## Versioning

Minor version numbers (0.0.x) are used for changes that are API compatible.  You should be able to upgrade between minor point releases without any other code changes.

Medium version numbers (0.x.0) may include API changes, in line with the [deprecation policy][deprecation-policy].  You should read the release notes carefully before upgrading between medium point releases.

Major version numbers (x.0.0) are reserved for substantial project milestones.

### 0.3.8

**Date:** [22th August 2019]

* BUG. Fix `aiohttp` dispatch return JsonResponse arguments.

### 0.3.7

**Date:** [15th August 2019]

* Change `@asyncio.coroutine` to `async/await`.

### 0.3.6

**Date:** [14th August 2019]

* Fix for current remove fields from base serializer.
```python
class Ser(Serializer):
    field_one = CharField()

class TwoSer(Ser):
    field_one = None

```

### 0.3.5

**Date:** [22th Jule 2019]

* Fix for current work [`source`][SourceFieldAttribute] attribute for base fields class.
* Fix exceptions `__str__` method.
* Fix `GenericViews` `MRO`.
* Added unbound `response_class` from all views.
* Fix `ValidationError` arguments in views.

### 0.3.4

**Date:** [22th Jule 2019]

* Added [`source`][SourceFieldAttribute] attribute for base fields class.

### 0.3.3

**Date:** [22th Jule 2019]

* Finish fix setup.py config. Change travis config, codecov config.

### 0.3.2

**Date:** [22th Jule 2019]

* Mini fix new setup.py config. Added requirements folder to `data_files` argument.

### 0.3.1

**Date:** [22th Jule 2019]

* Mini fix new setup.py config. Change requirements

### 0.3.0

**Date:** [19th Jule 2019]

* Added [`base views`][BaseViews]
* Added [`base views mixins`][ViewsMixins]
* Added [`views pagination`][ViewsPaginations]
* Added ApiException
* Added [`views for Flask`][FlaskViews]
* Added [`views for AioHttp`][AioHttpViews]
* Added [`views for Sanic`][SanicViews]
* Added utils.decorators for class check attributes and signature
* Fix not actual docs

### 0.2.2

**Date:** [15th Jule 2019]

* Added [`ChoiceValidator`][ChoiceValidator] in [`serializers.validators`][Validators].

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


[SourceFieldAttribute]: api-guid/fields#source
[BaseViews]: api-guid/views/views
[ViewsMixins]: api-guid/views/mixins
[ViewsPaginations]: api-guid/views/paginations
[FlaskViews]: api-guid/views/flask
[AioHttpViews]: api-guid/views/aiohttp
[SanicViews]: api-guid/views/sanic
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
[ChoiceValidator]: api-guid/validators.md#choicevalidator
[Serializers]: api-guid/serializers.md
[Validators]: api-guid/validators.md