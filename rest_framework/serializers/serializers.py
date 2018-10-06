"""
Сериалайзеры.

"""
import collections

import six

from flask_rest_framework.serializers.fields import Field
from flask_rest_framework.exceptions import ValidationError, FieldSearchError


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
                attr_obj.bind(attr_name, cls)

        # Пробрасываем хранилище филдов в сам класс.
        attrs.update(dict(_dict_fields=_dict_fields))

        return super().__new__(cls, name, bases, attrs)


class Serializer(six.with_metaclass(BaseSerializerMeta, Field)):
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

    def to_internal_value(self, data):
        """
        Преобразование данных в python объект.

        :param dict data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: dict

        """
        res, errors = {}, {}  # Заводим хранилища под результаты.

        for field_name, field_obj in self._dict_fields.items():
            # Валидируем каждое поле.
            src_value = data.get(field_name, None)

            try:
                # Сначала валидируем валидаторами филда.
                validated_value = field_obj.run_validation(src_value)

                # Теперь смотрим, если есть метод ручной валидации, вызываем его.
                validated_value = self._manual_validate_method(field_name, validated_value)

            except ValidationError as e:
                # Запоминаем ошибку валидации.
                errors[field_name] = e.detail

            else:
                # Запоминаем результат только тогда, когда было передано исходное значение.
                if src_value is not None:
                    res[field_name] = validated_value

        # Если преобразование и валидация прошли неуспешно.
        if errors:
            raise ValidationError(errors)

        # Возвращаем преобразованные и провалидированные данные.
        return res

    def to_representation(self, instance):
        """
        Преобразование объекта в валидный JSON объект.

        :param object instance: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: dict

        """
        res = {}  # Хранилище атрибутов.

        for field_name, field_val in self._dict_fields.items():
            # Пробуем достать атрибут.
            try:
                attribute = field_val.get_attribute(instance)
            except FieldSearchError:
                continue

            # Пробуем его превратить в JSON валидный формат.
            res[field_name] = field_val.to_representation(attribute)

        # Возвращаем.
        return res

    def _manual_validate_method(self, field_name, validated_value):
        """
        Ручная валидация конкретного филда.

        :param str field_name: Название филда.
        :param object validated_value: Значение филда.

        :return: Провалидированное значение.
        :rtype: object

        """
        # Теперь смотрим, если есть метод ручной валидации, вызываем его.
        manual_validate_method = getattr(self, 'validate_' + field_name, None)
        if callable(manual_validate_method):
            validated_value = manual_validate_method(validated_value)
        return validated_value

    def _field_validation(self):
        """
        Валидируем все филды.

        """
        # Бежим по филдам.
        for field_name, field_obj in self._dict_fields.items():
            try:
                # Преобразуем в питон тип и валидируем каждое поле.
                validated_val = field_obj.run_validation(self.initial_data.get(field_name, None))

                # Теперь ручная валидация.
                validated_val = self._manual_validate_method(field_name, validated_val)

                # И если во входящих данных было поле, тогда сохраняем в преобразованном виде.
                if field_name in self.initial_data:
                    self._validated_data[field_name] = validated_val

            except ValidationError as e:
                # Если не прошло валидацию, сохраняем ошибку.
                self._validated_data = {}
                self._errors[field_name] = e.detail

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

        # Валидируем все филды.
        self._field_validation()

        # Теперь прогоням метод полной ручной валидации.
        try:
            self._validated_data = self.validate(self._validated_data) if not self._errors else self._validated_data
        except ValidationError as e:
            self._errors['errors'] = e.detail

        # Если надо швырануть ошибку, швыряем.
        if self._errors and raise_exception:
            self._validated_data = {}
            raise ValidationError(self._errors)

        # Возвращаем результат валидации.
        return not bool(self._errors)

    def run_validation(self, data):
        """
        Запускает валидацию по текущему сериалайзеру.

        :param object data: Данные для валидации.

        :return: Провалидированное и преобразованное значение.
        :rtype: dict

        """
        # Сначала проверяем, не пришло ли пустое поле?
        is_empty, data = self.validate_empty_values(data)

        # Преобразуем в питон тип.
        value = self.to_internal_value(data)

        # Валидируем валидаторами.
        try:
            self.run_validators(value)
            value = self.validate(value)
            assert value is not None, '.validate() должен вернуть провалидированное значение'

        except ValidationError as e:
            raise ValidationError(detail=e.detail)

        # Возвращаем провалидированное и преобразованное значение.
        return value

    def validate(self, data):
        """
        Ручная валидация всех данных сериалайзера.

        :param dict data: Преобразованные и провалидированные данные, для ручной валидации.

        :return: Провалидированные данные. Осторожней, вернуть обязательно.
        :rtype: dict

        """
        return data

    @property
    def validated_data(self):
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

    @property
    def fields(self):
        """
        Поля сериалайзера.

        :return: Словарь полей сериалайзера.
        :rtype: dict

        """
        return self._dict_fields.copy()

    @property
    def data(self):
        """
        Серилизованный объект.

        :return: Серилизованный объект.
        :rtype: dict

        """
        if hasattr(self, 'initial_data') and not hasattr(self, '_validated_data'):
            msg = (
                'Когда сериалайзеру передается аргумент `data`'
                'должен быть вызван `.is_valid()` перед тем как получить доступ к '
                'серилизованным `.data` данным.\n'
                'Вы должны либо изначально вызвать `.is_valid()` или '
                'использовать `.initial_data`.'
            )
            raise AssertionError(msg)

        if not hasattr(self, '_data'):
            if self._instance is not None and not getattr(self, '_errors', None):
                self._data = self.to_representation(self._instance)
            elif hasattr(self, '_validated_data') and not getattr(self, '_errors', None):
                self._data = self.to_representation(self._validated_data)
            else:
                self._data = self.get_default()
        return self._data
