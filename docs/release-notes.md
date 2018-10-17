# Release Notes

## Versioning

Minor version numbers (0.0.x) are used for changes that are API compatible.  You should be able to upgrade between minor point releases without any other code changes.

Medium version numbers (0.x.0) may include API changes, in line with the [deprecation policy][deprecation-policy].  You should read the release notes carefully before upgrading between medium point releases.

Major version numbers (x.0.0) are reserved for substantial project milestones.

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
[TimeField]: api-guid/fields.md#-timefield
[DateTimeField]: api-guid/fields.md#-datetimefield
[ListField]: api-guid/fields.md#-listfield
