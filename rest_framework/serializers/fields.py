"""
Филды для сериалайзера.

"""
import re
import collections

import six

from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError
from rest_framework.utils import html
from rest_framework.serializers.validators import (
    RequiredValidator, MaxLengthValidator, MinLengthValidator, MaxValueValidator, MinValueValidator
)

MISSING_ERROR_MESSAGE = (
    'Выброшено ValidationError исключение для `{class_name}`, '
    'но ключа `{key}` не найдено в словаре `error_messages`.'
)  # Дефолтное сообщение об ошибке, для случаев когда нет сообщения.


def get_attribute(obj, attr_name):
    """
    Возвращаем атрибут объекта. Умеет работать со словарями.

    :param object obj: Объект, у которго ищем атрибут.
    :param str attr_name: Название атрибута.

    :return: Найденный атрибут либо исключение.
    :rtype: object

    :raise AttributeError: Если не нашли атрибут.

    """
    # Ищем атрибут.
    if isinstance(obj, collections.Mapping):
        attr = obj[attr_name]
    else:
        attr = getattr(obj, attr_name)

    # Возвращаем.
    return attr


class Field(object):
    """
    Базовый филд.

    """
    default_error_messages = {
        'required': 'Это поле обязательное.',
        'null': 'Это поле не может быть null.'
    }
    default_validators = []  # Дефолтный валидаторы для поля.

    def __init__(self, required=True, default=None, label=None, validators=None, error_messages=None):
        """
        Базовый филд.

        :param bool required: Обязательное ли поле.
        :param object default: Значение по умолчанию. Если установлено, тогда поле необязательное.
        :param str label: Название поля.
        :param list validators: Список валидаторов для поля.
        :param dict error_messages: Словарь с кастомным описанием ошибок.

        """
        self.label = label
        self.default = default
        self.required = bool(required) if self.default is None else False
        # Добаляем валидатор для обязательности поля.
        self._validators = ([RequiredValidator()] if self.required else []) + (validators or [])[:]

        # Формируем словарь с ошибками.
        messages = {}
        for cls in reversed(self.__class__.__mro__):
            messages.update(getattr(cls, 'default_error_messages', {}))
        messages.update(error_messages or {})
        self.error_messages = messages

    def bind(self, field_name, parent):
        """
        Инициализирует имя поля и экземпляр родителя.
        Вызывается когда поле добавляется к экземпляру родителя.

        :param str field_name: Название поля.
        :param Serializer parent: Класс сериалайзера, на котором находиться филд.

        :return:

        """
        self.field_name = field_name
        self.parent = parent

        # Сами ставим label, если его нету.
        if self.label is None:
            self.label = field_name.replace('_', ' ').capitalize()

    @property
    def validators(self):
        """
        :return: Список валидаторов поля.
        :rtype: list

        """
        if not hasattr(self, '_validators'):
            self._validators = self.get_validators()
        return self._validators

    @validators.setter
    def validators(self, validators):
        """
        Даем доступ к изменению списка валидаторов.

        :param list validators: Новый список валидаторов.

        """
        self._validators = validators

    def get_validators(self):
        """
        Возвращает дефолтные валидаторы.
        Используется для формирования списка валидаторовЮ если они не определены явно.

        :return: Список дефолтных валидаторов.
        :rtype: list

        """
        return self.default_validators[:]

    def fail(self, key, **kwargs):
        """
        Кидаем нормальную ошибку, если что то пошло не так во время обработки данных.

        :param str key: Тип ошибки. Ключ для словаря self.default_error_messages
        :param kwargs: Данные для форматирования сообщение о ошибке.

        :return:

        """
        # Пробуем достать сообщение об ошибке.
        try:
            msg = self.error_messages[key]
        except KeyError:
            # Если не смогли говорим об этом, использую общее сообщение.
            class_name = self.__class__.__name__
            msg = MISSING_ERROR_MESSAGE.format(class_name=class_name, key=key)
            raise AssertionError(msg)

        # Форматируем сообщение и кидаем ошибку.
        message_string = msg.format(**kwargs)
        raise ValidationError(message_string, code=key)

    def to_internal_value(self, data):
        """
        Преобразование данных в python объект.

        :param object data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: object

        """
        raise NotImplementedError('`to_internal_value()` должен быть определен.')

    def to_representation(self, value):
        """
        Преобразование объекта в валидный JSON объект.

        :param object value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: object

        """
        raise NotImplementedError('`to_representation()` должен быть определен.')

    def get_default(self):
        """
        Возвращаем дефолтное значение.
        Если необходимо, изначально вызываем callable объект для получения дефолтного значениея.

        :return: Дефолтное значение.
        :rtype: object

        """
        if callable(self.default):
            return self.default()
        return self.default

    def get_attribute(self, instance):
        """
        Ищет и возвращает атрибут у объекта.

        :return: Атрибут объекта.
        :rtype: object

        :raise ValidationError: Если не удалось найти поле.
        :raise Exception: Если во время поиска возникла ошибка.

        """
        try:
            # Пробуем достать данные.
            return get_attribute(instance, self.field_name)
        except (KeyError, AttributeError) as e:
            # Если есть дефолтное значение, тогда его.
            if self.default is not None:
                return self.get_default()
            # Если нет дефолтного и поле обязательное, ругаемся.
            if self.required:
                raise SkipError(self.error_messages['required'])

            # Иначе сообщаем об этом инциденте разработчику.
            msg = (
                'Выброщено {exc_type} при попытке получить значение для поля '
                '`{field}` у сериалайзера `{serializer}`.\nВозможно поле '
                'сериалайзера названо неверно и не соотвествует ни одному '
                'атрибуту или ключу у объекта `{instance}`.\n'
                'Текст оригинального исключения: {exc}.'.format(
                    exc_type=type(e).__name__,
                    field=self.field_name,
                    serializer=self.parent.__name__,
                    instance=instance.__class__.__name__,
                    exc=e
                )
            )
            raise type(e)(msg)

    def validate_empty_values(self, data):
        """
        Смотрит, пустое ли пришло значение.

        :param object data: Данные для проверки.

        :return: Результат проверки, и актуальные данные.
                 Если есть дефолтное значение и не передано ничего, возвращает дефолтное.
                 Кортеж: (is None, actual data)
        :rtype: tuple
        :raise ValidationError: Если валидацию на пустое поле не прошли.

        """
        # Обрабатываем.
        is_empty, data = data is None, data if data is not None else self.default

        # Валидируем.
        if is_empty and not self.required:
            return is_empty, data

        # Если пустое и оно не обязательно, тогад нечего тут валидировать и преобразовывать.
        if is_empty:
            raise ValidationError(self.error_messages['required'])

        # Возвращаем.
        return is_empty, data

    def run_validation(self, data):
        """
        Запускает преобразование данных потом валидацию.

        :param object data: Данные, которые стоит провалидировать, преобразовать и т.д.

        :return: Преобразованные провалидированные данные.
        :rtype: object

        :raise ValidationError: Если поле не прошло валидацию.

        """
        # Сначала валидируем на обязательность.
        is_empty, data = self.validate_empty_values(data)

        # Обрабатываем сырые данные.
        value = self.to_internal_value(data)
        # Запускаем валидаторы.
        self.run_validators(value)

        return value

    def run_validators(self, value):
        """
        Валидирует данные по всем валидаторам филда

        :param object value: Данные для валидации.

        :raise ValidationError: Если валидацию не прошли.

        """
        errors = []

        for validator in self.validators or []:
            try:
                # Прогоняем каждым сериалайзером.
                validator(value)
            except ValidationError as e:
                errors.append(e.detail)

        # Проверяем на ошибки.
        if errors:
            raise ValidationError(errors)


class CharField(Field):
    """
    Филд для текста.

    """
    default_error_messages = {
        'invalid': 'Не валидная строка.',
        'blank': 'Это поле не может быть пустым.',
        'min_length': 'Значение должно быть длиннее {min_length} символов.',
        'max_length': 'Значение должно быть короче {max_length} символов.'
    }

    def __init__(self, min_length=None, max_length=None, trim_whitespace=False, allow_blank=True, *args, **kwargs):
        """
        Филд для текста.

        :param int min_length: Минимальная длина строки.
        :param int max_length: Максимальная длина строки.
        :param bool trim_whitespace: Обрезать ли пробелы в начале и конце строки?
        :param bool allow_blank: Разрешить ли пустую строку?

        """
        super().__init__(*args, **kwargs)
        self.max_length = max_length
        self.min_length = min_length
        self.trim_whitespace = trim_whitespace
        self.allow_blank = allow_blank

        # Добавляем валидаторы.
        if self.max_length:
            message = self.error_messages['max_length'].format(max_length=self.max_length)
            self.validators.append(MaxLengthValidator(max_length, message=message))
        if self.min_length:
            message = self.error_messages['min_length'].format(min_length=self.min_length)
            self.validators.append(MinLengthValidator(self.min_length, message=message))

    def run_validation(self, data=None):
        """
        Проверяем на пустую строку тут, что бы она не проваливалась в подклассы в `.to_internal_value()`.

        :param object data: Данные для валидации.

        :return: Провалидированные обработанные данные.
        :rtype: str

        """
        if data == '' or (self.trim_whitespace and six.text_type(data).strip() == ''):
            if not self.allow_blank:
                self.fail('blank')
            return ''
        return super(CharField, self).run_validation(data)

    def to_internal_value(self, data):
        """
        Преобразование данных в python str объект.

        :param object data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: str

        """
        # Числа как строки пропускаем, но bool как строки кажется уже ошибка разработчика.
        if isinstance(data, bool) or not isinstance(data, six.string_types + six.integer_types + (float,)):
            self.fail('invalid')
        return six.text_type(data)

    def to_representation(self, value):
        """
        Преобразование объекта в валидный str объект.

        :param object value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: str

        """
        return six.text_type(value)


class IntegerField(Field):
    """
    Филд для целого числа.

    """
    default_error_messages = {
        'invalid': 'Не валидное значение.',
        'min_value': 'Значение должно быть больше или равно {min_value}.',
        'max_value': 'Значение должно быть меньше или равно {max_value}.',
        'max_string_length': 'Строка слишком длинная.'
    }
    MAX_STRING_LENGTH = 1000  # Ограничиваем максимальный размер числа.
    re_decimal = re.compile(r'\.0*\s*$')  # '1.0' это инт, а это не инт '1.2'

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        """
        Филд для целого числа.

        :param int min_value: Минимальное значение.
        :param int max_value: Максимальное значение.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value if min_value is None else int(min_value)
        self.max_value = max_value if max_value is None else int(max_value)

        # Добавляем валидаторы.
        if self.min_value:
            message = self.error_messages['min_value'].format(min_value=self.min_value)
            self.validators.append(MinValueValidator(self.min_value, message=message))
        if self.max_value:
            message = self.error_messages['max_value'].format(max_value=self.max_value)
            self.validators.append(MaxValueValidator(self.max_value, message=message))

    def to_internal_value(self, data):
        """
        Преобразование данных в python int объект.

        :param Union[str, int, float] data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: int

        """
        # Смотрим, не хотят ли нам память забить?
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            data = int(self.re_decimal.sub('', str(data)))
        except (ValueError, TypeError):
            self.fail('invalid')
        return data

    def to_representation(self, value):
        """
        Преобразование объекта в валидный int объект.

        :param int value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: int

        """
        return int(value)


class FloatField(Field):
    """
    Филд для числа с плавающей точкой.

    """
    default_error_messages = {
        'invalid': 'Не валидное значение.',
        'min_value': 'Значение должно быть больше или равно {min_value}.',
        'max_value': 'Значение должно быть меньше или равно {max_value}.',
        'max_string_length': 'Строка слишком длинная.'
    }
    MAX_STRING_LENGTH = 1000  # Ограничиваем максимальный размер числа.

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        """
        Филд для числа с плавающей точкой.

        :param float min_value: Минимальное значение.
        :param float max_value: Максимальное значение.

        """
        super().__init__(*args, **kwargs)
        self.min_value = min_value if min_value is None else int(min_value)
        self.max_value = max_value if max_value is None else int(max_value)

        # Добавляем валидаторы.
        if self.min_value:
            message = self.error_messages['min_value'].format(min_value=self.min_value)
            self.validators.append(MinValueValidator(self.min_value, message=message))
        if self.max_value:
            message = self.error_messages['max_value'].format(max_value=self.max_value)
            self.validators.append(MaxValueValidator(self.max_value, message=message))

    def to_internal_value(self, data):
        """
        Преобразование данных в python float объект.

        :param Union[str, int, float] data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: float

        """
        # Смотрим, не хотят ли нам память забить?
        if isinstance(data, six.text_type) and len(data) > self.MAX_STRING_LENGTH:
            self.fail('max_string_length')

        try:
            return float(data)
        except (TypeError, ValueError):
            self.fail('invalid')

    def to_representation(self, value):
        """
        Преобразование объекта в валидный int объект.

        :param float value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: float

        """
        return float(value)


class BooleanField(Field):
    """
    Филд для boolean типа.

    """
    default_error_messages = {
        'invalid': '"{input}" должен быть валидным boolean типом.'
    }
    TRUE_VALUES = {
        't', 'T',
        'y', 'Y', 'yes', 'YES', 'Yes',
        'true', 'True', 'TRUE',
        'on', 'On', 'ON',
        '1', 1,
        True
    }  # Словарь с True вариантами.
    FALSE_VALUES = {
        'f', 'F', 'n',
        'N', 'no', 'NO', 'No',
        'false', 'False', 'FALSE',
        'off', 'Off', 'OFF',
        '0', 0, 0.0,
        False
    }  # Словарь с False вариантами.
    NULL_VALUES = {'n', 'N', 'null', 'Null', 'NULL', '', None}  # Словарь с NULL вариантами.

    def to_internal_value(self, data):
        """
        Преобразование данных в python bool объект.

        :param bool data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: bool

        """
        try:
            if data in self.TRUE_VALUES:
                return True
            elif data in self.FALSE_VALUES:
                return False
            elif data in self.NULL_VALUES:
                return None
        except TypeError:  # Если пришел не хэшируемый тип.
            pass
        self.fail('invalid', input=data)

    def to_representation(self, value):
        """
        Преобразование объекта в валидный bool объект.

        :param bool value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: bool

        """
        # Сначала ищем в таблице соотвествий.
        if value in self.NULL_VALUES:
            return None
        if value in self.TRUE_VALUES:
            return True
        elif value in self.FALSE_VALUES:
            return False
        # Если не нашли, пробуем сами преобразовать.
        return bool(value)


class ListField(Field):
    """
    Филд для списка объектов.

    """
    default_error_messages = {
        'not_a_list': 'Ожидался массив элементов но получен "{input_type}".',
        'empty': 'Массив не может быть пустым.',
        'min_length': 'Длина массива должна быть больше или равна {min_length} элементов.',
        'max_length': 'Длина массива должна быть меньше или равна {max_length} элементов.'
    }
    child = None

    def __init__(self, child=None, min_length=None, max_length=None, allow_empty=False, *args, **kwargs):
        """
        Филд для списка объектов.

        :param rest_framework.serializers.Field child: Филд, описывающий тип элементов массива.
        :param int min_length: Минимальная длина массива.
        :param int max_length: Максимальная длина массива.
        :param bool allow_empty: Разрешить ли пустой массив?

        """
        super().__init__(*args, **kwargs)
        self.child = child
        self.min_length = min_length
        self.max_length = max_length
        self.allow_empty = bool(allow_empty)

        # Проверяем поле child.
        if all((not isinstance(child, Field), not isinstance(self.child, Field))):
            raise TypeError('`child=` должен быть экземпляром rest_framework.serializers.Field класса.')
        self.child.bind(field_name='', parent=self)  # Биндим child поле.

        # Добавляем валидаторы.
        if self.max_length:
            message = self.error_messages['max_length'].format(max_length=self.max_length)
            self.validators.append(MaxLengthValidator(max_length, message=message))
        if self.min_length:
            message = self.error_messages['min_length'].format(min_length=self.min_length)
            self.validators.append(MinLengthValidator(self.min_length, message=message))

    def to_internal_value(self, data):
        """
        Преобразование данных в python list объект.

        :param iter data: Данные для преобразования.

        :return: Преобразованные данные.
        :rtype: list

        """
        if html.is_html_input(data):
            data = html.parse_html_list(data)

        if any((isinstance(data, type('')), isinstance(data, collections.Mapping), not hasattr(data, '__iter__'))):
            self.fail('not_a_list', input_type=type(data).__name__)

        if not self.allow_empty and len(data) == 0:
            self.fail('empty')

        return [self.child.run_validation(item) for item in data]

    def to_representation(self, value):
        """
        Преобразование объекта в валидный json list объект.

        :param list value: Объект, который стоит преобразовать.

        :return: Преобразованные данные.
        :rtype: list

        """
        return [self.child.to_representation(item) if item is not None else None for item in value]
