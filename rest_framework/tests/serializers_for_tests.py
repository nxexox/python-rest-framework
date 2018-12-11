"""
Serializers for tests.

"""

from rest_framework.serializers.fields import (
    CharField, IntegerField, FloatField, BooleanField, ListField, SerializerMethodField
)
from rest_framework.serializers.serializers import Serializer


class SerializerPrimitiveField(Serializer):
    """
    Serializer for primitive fields.

    """
    char_f = CharField(required=True)
    integer_f = IntegerField(required=True)
    float_f = FloatField(required=True)
    bool_f = BooleanField(required=True)
    list_f = ListField(child=CharField(required=True), required=True)


class SerializerMixinSingle(Serializer):
    """
    Serializer for deep field.

    """
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField()


class SerializerMixinMany(Serializer):
    """
    Serializer for deep list field.

    """
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField(many=True)


class SerializerMixinRequired(Serializer):
    """
    Serializer for deep required field.

    """
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField(required=True)


class SerializerMethodFieldDefault(Serializer):
    """
    Serializer for default methods field.

    """
    test = SerializerMethodField()

    def get_test(self, obj):
        return obj

    def pop_test(self, data):
        return data


class SerializerMethodFieldSingle(Serializer):
    """
    Serializer for one method for two situation.

    """
    test = SerializerMethodField('test_test', 'test_test')

    def test_test(self, obj):
        return obj


class InheritSerRoot(Serializer):
    """
    Check inherit. Root serializer.

    """
    root = IntegerField(required=True)


class InheritFirstLevelChild(InheritSerRoot):
    """
    Check inherit. First level inherit serializer.

    """
    first_level_child = IntegerField(required=True)


class InheritSecondLevelChild(InheritFirstLevelChild):
    """
    Check inherit. Second level inherit serializer.

    """
    second_level_child = IntegerField(required=True)
