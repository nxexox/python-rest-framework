# flask-rest-framework
Flask Rest Framework

## Сделали:

* Базовый филд, и пару филдов для тестирования.
* Базовый сериалайзер.
* Базовую логику взаимодействия филдов сериалайзеров и валидаторов.

## TODO:

* Сериалайзер должен вести себя как поле, что бы можно было делать вложенность
* Научить сериалайзер работать не с одним объектом а с множеством. many=True
* Написать APIView, и все CRUDGenericView
* Научиться парсить тело запроса что бы преобразовывать в валидный дикт и пробрасывать в сериалайзер
* Научиться делать хэндлеры с ошибками и выбрасывать их через self.fail или Исключение

* + Научиться понимать что данные неверные до того, как мы пробрасываем их в валидаторы
* + Сериалайзер должен вести себя как поле, что бы можно было делать вложенность
* + Научить сериалайзер object -> dict
*   Научиться вложенные сериалайзеры работать как обязательные.
*   Научить сериалайзер работать не с одним объектом а с множеством. many=True
*   Написать APIView, и все CRUDGenericView
*   Научиться парсить тело запроса что бы преобразовывать в валидный дикт и пробрасывать в сериалайзер
*   Научиться делать хэндлеры с ошибками и ывбрасывать их через self.fail или Исключение



```python
>>> from rest_framework.serializers.serializers import Serializer
>>> from rest_framework.serializers.fields import CharField, IntegerField

class Test(Serializer):
    char_field = CharField(required=False, min_length=10)
    int_field = IntegerField(required=True)

ser = Test(data={field_name: field_value,...})
res_valid = ser.is_valid()  # ser.is_valid(raise_exception=True)

if res_valid:
    print(ser.validated_data)
else:
    print(ser.errors)

```