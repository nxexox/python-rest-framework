"""
Сериалайзеры.

"""
import copy
import inspect
from collections import OrderedDict

import six

from rest_framework.serializers.fields import Field
from rest_framework.exceptions import ValidationError, SkipError
from rest_framework.utils import html


LIST_SERIALIZER_KWARGS = (
    'required', 'default', 'label', 'error_messages', 'allow_empty',
    'instance', 'data', 'min_length', 'max_length'
)  # Список аргументов, для ListSerializer, что бы контролировать создание many=True.


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
        _dict_fields = OrderedDict()  # Заводим хранилище филдов.

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


class BaseSerializer(six.with_metaclass(BaseSerializerMeta, Field)):
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

    def __new__(cls, *args, **kwargs):
        """
        Автоматически создаем классы для `many=True`,

        # :param bool many: Флаг, указывающий это объект будет один или несколько?

        """
        many = kwargs.pop('many', False)
        if bool(many):
            return cls.many_init(*args, **kwargs)
        return super(BaseSerializer, cls).__new__(cls)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        Этот метод реализует создание родительского класса `ListSerializer`,
        когда используется `many=True`. Вы можете настроить его, если вам нужно определить,
        какие аргументы ключевого слова переданы родительскому элементу,
        и какие передаются дочернему элементу.

        """
        child_serializer = cls(*args, **kwargs)  # Создаем child сериалайзер.

        # Пробрасываем аргументы к ListSerializer.
        list_kwargs = {'child': child_serializer}
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })

        # Создаем ListSerializer.
        return ListSerializer(*args, **list_kwargs)

    def validate(self, data):
        """
        Ручная валидация всех данных сериалайзера.

        :param dict data: Преобразованные и провалидированные данные, для ручной валидации.

        :return: Провалидированные данные. Осторожней, вернуть обязательно.
        :rtype: dict

        """
        return data

    def to_internal_value(self, data):
        """
        Преобразование данных в python объект.

        :param dict data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: dict

        """
        raise NotImplementedError('Необходимо реализовать метод `.to_internal_value()`.')

    def to_representation(self, instance):
        """
        Преобразование объекта в валидный JSON объект.

        :param object instance: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: dict

        """
        raise NotImplementedError('Необходимо реализовать метод `.to_representation()`.')

    def is_valid(self, raise_exception=False):
        """
        Валидирует данные, пришедшие в сериалайзер.

        :param bool raise_exception: Швырять ли исключение если валидация не прошла?

        :return: Результат валидации.
        :rtype: bool

        """
        raise NotImplementedError('Необходимо реализовать метод `.is_valid()`.')

    @property
    def validated_data(self):
        """
        Провалидированные данные.

        :return: Провалидированные данные.
        :rtype: dict

        """
        raise NotImplementedError('Необходимо реализовать свойство `.validated_data`.')

    @property
    def errors(self):
        """
        Ошибки во время валидации.

        :return: Ошибки во время валидации.
        :rtype: dict

        """
        raise NotImplementedError('Необходимо реализовать свойство `.errors`.')

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


class Serializer(BaseSerializer):
    """
    Базовый класс сериалайзера.

    """
    def to_internal_value(self, data):
        """
        Преобразование данных в python объект.

        :param dict data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: dict

        """
        return self._field_validation(self._dict_fields, data)

    def to_representation(self, instance):
        """
        Преобразование объекта в валидный JSON объект.

        :param object instance: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: dict

        """
        res = OrderedDict()  # Хранилище атрибутов.

        for field_name, field_val in self._dict_fields.items():
            # Пробуем достать атрибут.
            try:
                attribute = field_val.get_attribute(instance)
            except SkipError:
                # TODO: Ту делема, кидать ошибку, если атрибута у объекта не нашли, или скипать?
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

    def _field_validation(self, fields_dict, data):
        """
        Валидируем все филды.

        :param dict fields_dict: Словарь с проинициализированными филдами, по которым валидируем.
        :param dict data: Данные, которые валидируем.

        :return: Провалидированные и обрабоатанные даные.
        :raise ValidationError: Если произошли ошибки во время валидации.

        """
        validated_data, errors = OrderedDict(), OrderedDict()
        # Бежим по филдам.
        for field_name, field_obj in fields_dict.items():
            try:
                # Преобразуем в питон тип и валидируем каждое поле.
                validated_val = field_obj.run_validation(data.get(field_name, None))

                # Теперь ручная валидация.
                validated_val = self._manual_validate_method(field_name, validated_val)

                # И если во входящих данных было поле, тогда сохраняем в преобразованном виде.
                if field_name in data or field_obj.default:
                    validated_data[field_name] = validated_val or field_obj.default

            except ValidationError as e:
                # Если не прошло валидацию, сохраняем ошибку.
                errors[field_name] = e.detail

        if any(errors):
            raise ValidationError(errors)

        return validated_data

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
        self._errors, self._validated_data = OrderedDict(), OrderedDict()

        # Валидируем все филды.
        try:
            self._validated_data = self._field_validation(self._dict_fields, self.initial_data)
        except ValidationError as e:
            self._errors = e.detail

        # Теперь прогоням метод полной ручной валидации.
        try:
            self._validated_data = self.validate(self._validated_data) if not self._errors else self._validated_data
        except ValidationError as e:
            self._errors['errors'] = e.detail

        # Если надо швырануть ошибку, швыряем.
        if self._errors and raise_exception:
            self._validated_data = OrderedDict()
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


class ListSerializer(Serializer):
    """
    Сериалайзер для списка объектов.

    """
    # TODO: Переписать заново вместе с many_init.
    child = None  # Дочерний сериалайзер.

    default_error_messages = {
        'not_a_list': 'Ожидался массив элементов но получен "{input_type}".',
        'empty': 'Массив не может быть пустым.',
    }

    def __init__(self, child=None, allow_empty=None, *args, **kwargs):
        """
        Сериалайзер для множества объектов.

        :param rest_framework.serializers.Field child: Дочерний сериалайзер.
        :param bool allow_empty: Разрешить ли пустой массив.

        """
        self.child = child or copy.deepcopy(self.child)
        self.allow_empty = bool(allow_empty)

        # Чекаем, что данные корректные.
        assert self.child is not None, '`child` обязательный аргумент.'
        assert not inspect.isclass(self.child), '`child` должен быть инициализирован.'

        # инициализируем сериалайзер.
        super(ListSerializer, self).__init__(*args, **kwargs)
        # Биндим дочерний элемент.
        self.child.bind(field_name='', parent=self)

    def to_internal_value(self, data):
        """
        Преобразование данных в python list объект.

        :param object data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: list

        """
        # Парсим данные.
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        # Превоначальная валидация что пришел массив.
        if not isinstance(data, list):
            message = self.error_messages['not_a_list'].format(
                input_type=type(data).__name__
            )
            raise ValidationError({'non_field_errors': [message]}, code='not_a_list')

        # Валидация, что это не пустое значение и можно ли пустое.
        if not self.allow_empty and len(data) == 0:
            message = self.error_messages['empty']
            raise ValidationError({'non_field_errors': [message]}, code='empty')

        res, errors = [], []  # Заводим хранилища под результаты.

        # Валидируем каждый элемент из списка.
        for item in data:
            try:
                value = self.child.run_validation(item)
            except ValidationError as e:
                res.append({})
                errors.append(e.detail)
            else:
                res.append(value)
                errors.append({})

        # Если преобразование и валидация прошли неуспешно.
        if any(errors):
            raise ValidationError(errors)

        # Возвращаем преобразованные и провалидированные данные.
        return res

    def to_representation(self, instance):
        """
        Преобразование объекта в валидный JSON list объект.

        :param list instance: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: list

        """
        return [self.child.to_representation(item) for item in instance]

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
        self._errors, self._validated_data = [], []

        # Валидируем все филды.
        try:
            self._validated_data = self.to_internal_value(self.initial_data)
        except ValidationError as e:
            self._errors = e.detail

        # Если надо швырануть ошибку, швыряем.
        if self._errors and raise_exception:
            self._validated_data = []
            raise ValidationError(self._errors)

        # Возвращаем результат валидации.
        return not bool(self._errors)

    @property
    def validated_data(self):
        """
        Провалидированные данные.

        :return: Провалидированные данные.
        :rtype: dict

        """
        if not hasattr(self, '_validated_data'):
            raise AssertionError('Для получения `.validate_data` нужно сначала вызвать `.is_valid()`.')
        return self._validated_data[:]

    @property
    def errors(self):
        """
        Ошибки во время валидации.

        :return: Ошибки во время валидации.
        :rtype: dict

        """
        if not hasattr(self, '_errors'):
            raise AssertionError('Для получения `.errors` нужно сначала вызвать `.is_valid()`.')
        return self._errors[:]
