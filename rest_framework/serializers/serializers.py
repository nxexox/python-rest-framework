"""
Сериалайзеры.

"""
import six

from rest_framework.serializers.fields import Field
from rest_framework.exceptions import ValidationError


class BaseSerializerMeta(type):
    """
    Метакласс для создания сериалайзеров.

    """
    def __new__(cls, name, bases, attrs):
        """
        Создаем список филдов у сериалайзера.

        :param str name: Название создаваемого класса.
        :param tuple bases: Кортеж базовых классов.
        :param dict attrs: Словарь атрибутов.

        """
        _dict_fields = {}  # Заводим хранилище филдов.

        # Заполняем хранилище филдов.
        for attr_name, attr_obj in attrs.items():
            # TODO: Добавить проверку на наличие атрибута.
            # Заполняем в хранилище
            if isinstance(attr_obj, Field):
                _dict_fields[attr_name] = attr_obj

        # Пробрасываем хранилище филдов в сам класс.
        attrs.update(dict(_dict_fields=_dict_fields))

        return super().__new__(cls, name, bases, attrs)


class Serializer(six.with_metaclass(BaseSerializerMeta)):
    """
    Базовый класс сериалайзера.

    """
    def __init__(self, instance=None, data=None, *args, **kwargs):
        """
        Создание сериалайзера. Сериалайзер должен вести себя как Field, что бы можно было делать вложенность.

        :param object instance: Python объект для преобразования.
        :param dict data: Данные, пришедшие в запросе.

        """
        super().__init__(*args, **kwargs)
        self._instance = instance
        if isinstance(data, dict):
            self.initial_data = data

    def to_representation(self, instance):
        """
        Преобразование объекта в валидный JSON объект.

        :param object instance: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: object

        """
        raise NotImplementedError('`to_representation()` должен быть определен.')

    def to_internal(self, data):
        """
        Преобразование данных в python объект.

        :param object data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: object

        """
        raise NotImplementedError('`to_internal_value()` должен быть определен.')

    def is_valid(self, raise_exception=False):
        """
        Валидирует данные, пришедшие в сериалайзер.

        :param bool raise_exception: Швырять ли исключение если валидация не прошла?

        :return: Результат валидации.
        :rtype: bool

        """
        if not hasattr(self, 'initial_data'):
            raise AssertionError('Для вызова `.is_valid()` необходимо передать `dict` в конструктор `data=`')

        # Готовим СТ для результатов.
        self._errors, self._validated_data = {}, {}

        # Бежим по всем полям сериалайзера.
        for attr_name, attr_obj in self._dict_fields.items():
            try:
                # Преобразуем в питон тип и валидируем каждое поле.
                validated_val = attr_obj.run_validation(self.initial_data.get(attr_name, None))

                # И если во входящих данных было поле, тогда сохраняем в преобразованном виде.
                if attr_name in self.initial_data:
                    self._validated_data[attr_name] = validated_val

            except ValidationError as e:
                # Если не прошло валидацию, сохраняем ошибку.
                self._validated_data = {}
                self._errors[attr_name] = e.detail
            else:
                self._errors = {}

        # Если надо швырануть ошибку, швыряем.
        if self._errors and raise_exception:
            raise ValidationError(self._errors)

        return not bool(self._errors)

    @property
    def validate_data(self):
        """
        Провалидированные данные.

        :return: Провалидированные данные.
        :rtype: dict

        """
        if not hasattr(self, '_validated_data'):
            raise AssertionError('Для получения `.validate_data` нужно сначала вызвать `.is_valid()`.')
        return self._validated_data.copy()

    @property
    def errors(self):
        """
        Ошибки во время валидации.

        :return: Ошибки во время валидации.
        :rtype: dict

        """
        if not hasattr(self, '_errors'):
            raise AssertionError('Для получения `.errors` нужно сначала вызвать `.is_valid()`.')
        return self._errors.copy()
