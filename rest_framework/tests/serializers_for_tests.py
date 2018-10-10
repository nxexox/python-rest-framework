"""
Сериалайзеры для теста.

"""

from rest_framework.serializers.fields import (
    CharField, IntegerField, FloatField, BooleanField, ListField
)
from rest_framework.serializers.serializers import Serializer


class SerializerPrimitiveField(Serializer):
    char_f = CharField(required=True)
    integer_f = IntegerField(required=True)
    float_f = FloatField(required=True)
    bool_f = BooleanField(required=True)
    list_f = ListField(child=CharField(required=True), required=True)


class SerializerMixinSingle(Serializer):
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField()


class SerializerMixinMany(Serializer):
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField(many=True)


class SerializerMixinRequired(Serializer):
    char_f = CharField(required=True)
    ser_f = SerializerPrimitiveField(required=True)
