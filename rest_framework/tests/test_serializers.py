"""
Тестирование сериалайзеров.
1. Тестируем отдельо методы и логику вызовов.
2. Тестируем внешний интерфейс, как они должны работать.

"""
import collections
from unittest import TestCase


from rest_framework.serializers.fields import (
    CharField, BooleanField, IntegerField, FloatField, ListField
)
from rest_framework.serializers.serializers import BaseSerializer, Serializer, ListSerializer
from rest_framework.exceptions import SkipError
from rest_framework.serializers.exceptions import ValidationError

from rest_framework.tests.serializers_for_tests import (
    SerializerPrimitiveField, SerializerMixinSingle, SerializerMixinMany, SerializerMixinRequired
)


class BaseSerializerTestClass(TestCase):
    """
    Класс для тестирования логики и методов сериалайзера.

    """
    serializer_class = BaseSerializer
    abstract_methods = {
        'to_internal_value': {'data': None},
        'to_representation': {'instance': None},
        'is_valid': {},
        'validated_data': {},
        'errors': {}
    }
    validate_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    to_internal_value_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    to_representation_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    is_valid_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    validated_data_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )
    errors = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )

    # Класс для тестирования на пустоту.
    class Empty:
        pass

    def create_params(self, **params):
        """
        Создание параметров, для создания сериалайзера.

        :return: Параметры для создания сериалайзера.
        :rtype: dict

        """
        return params

    def __test_method_cases(self, method_name):
        """
        Тестирование функции по кейсам.

        :param str method_name: Название метода, который стоит протестировать по кейсам.

        """
        # Проверяем все кейсы.
        for case in getattr(self, '%s_cases' % method_name, []):
            # Пропускаем тест.
            if not case:
                continue

            try:
                # Достаем данные.
                data, result = case.get('data', {}), case.get('return', None)
                params, exceptions = case.get('params', {}), case.get('exceptions', {})
                create_ser = case.get('create_ser', None)

                data = data or {}  # Превращаем None в словарь.

                # Строим сериалайзер и ищем метод для тестирования.
                if callable(create_ser):
                    serializer = create_ser(**self.create_params(**params))
                else:
                    serializer = self.serializer_class(**self.create_params(**params))

                method = getattr(serializer, method_name, self.Empty())
                if isinstance(method, self.Empty):
                    self.fail('Тестирование по кейсам не удалось. Не удалось найти метод `{}` у класса `{}`.'.format(
                        method_name, serializer.__class__.__name__
                    ))

                # Если ожидаются ошибки.
                if exceptions:
                    try:
                        res = method(**data) if callable(method) else method
                        self.fail('В методе `{}.{}()` кейс `{}` не выкинул исключение. Метод вернул: `{}`.'.format(
                            serializer.__class__.__name__, method_name, case, res
                        ))
                    except tuple(exceptions):
                        pass
                else:
                    # Если ошибок не ожидается.
                    res = method(**data) if callable(method) else method
                    assert res == result, \
                        'В методе `{}.{}()` кейс {} вернул неверный результат `{}`'.format(
                            serializer.__class__.__name__, method_name, case, res
                        )
            except Exception as e:
                self.fail('Во время проверки кейса `{}` для метода `{}.{}` произошла неожиданная ошибка: `{}: {}`'.format(
                    case, self.serializer_class.__class__.__name__, method_name, e.__class__.__name__, e
                ))

    def test_init(self):
        """
        Тестирование создания.

        """
        # Создаем без всего.
        ser = self.serializer_class()
        assert ser.instance is None, '`.instance` должен быть None. Он `{}`.'.format(ser.instance)
        assert getattr(ser, 'initial_data', None) is None, '`.initial_data` должен быть None. Он `{}`.'.format(
            getattr(ser, 'initial_data', None)
        )

        # Создаем с пустым объектом.
        obj = type('object', (object,), {})
        ser = self.serializer_class(obj)
        assert ser.instance == obj, '`.instance` должен быть {}. Он `{}`.'.format(obj, ser.instance)
        assert getattr(ser, 'initial_data', None) is None, '`.initial_data` должен быть None. Он `{}`.'.format(
            getattr(ser, 'initial_data', None)
        )

        # Создаем с данными.
        obj = {}
        ser = self.serializer_class(data=obj)
        assert ser.instance is None, '`.instance` должен быть None. Он `{}`.'.format(ser.instance)
        assert getattr(ser, 'initial_data', None) == obj, '`.initial_data` должен быть {}. Он `{}`.'.format(
            obj, getattr(ser, 'initial_data', None)
        )

    def test_validate_cases(self):
        """
        Тестируем проброс данных.

        """
        self.__test_method_cases('validate')

    def test_abstract_methods(self):
        """
        Тестирование абстрактных методов.

        """
        field = self.serializer_class(**self.create_params())
        for method_name, method_params in self.abstract_methods.items():
            try:
                # Работает как для методов, так и для абстрактных свойств.
                getattr(field, method_name, lambda: None)(**method_params)
                self.fail('Метод `.{}` должен выбрасывать исключение `NotImplementedError`.'.format(method_name))
            except NotImplementedError:
                pass

    def test_to_internal_value_cases(self):
        """
        Тестирование преобразования данных в python объект.

        """
        if 'to_internal_value' not in self.abstract_methods:
            self.__test_method_cases('to_internal_value')

    def test_to_representation_cases(self):
        """
        Тестирование реобрзования объектв в валидный JSON.

        """
        if 'to_representation' not in self.abstract_methods:
            self.__test_method_cases('to_representation')

    def test_is_valid_cases(self):
        """
        Тестирование валидации и обработки данных.

        """
        if 'is_valid' in self.abstract_methods:
            self.__test_method_cases('is_valid')

    def test_validated_data_cases(self):
        """
        Тестирование свойства валидатед дата.

        """
        if 'validated_data' not in self.abstract_methods:
            self.__test_method_cases('validated_data')

    def test_errors(self):
        """
        Тестирование свойства ошибок.

        """
        if 'errors' not in self.abstract_methods:
            self.__test_method_cases('errors')

    def test_fields(self):
        """
        Тестирование свойства филдов.

        """
        pass

    def test_data(self):
        """
        Тестирование свойства с провалидированными преобразованными данными.

        """
        pass


# TODO: Доделать кейсы.
class SerializerTestClass(TestCase):
    """
    Тестирование класса сериалайзера по методам.

    """
    serializer_class = Serializer
    abstract_methods = {}
    validate_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {'data': {'data': {}}, 'return': {}},
        {'data': {'data': None}, 'return': None},
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': 'qwe'}, 'return': 'qwe'}
    )
    to_internal_value_cases = (
        {},
    )
    to_representation_cases = (
        {},
    )
    is_valid_cases = (
        {},
    )
    validated_data_cases = (
        {},
    )
    errors = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки,
        # create_ser - функция, принимающая на вход params и озвращающяя сериалайзер, готовый для тестирования.
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': [], 'create_ser': lambda params: serializer}
        {},
    )

    def create_serializer(self):
        """
        Функция создания сериалайзера для последующего тестирования методов.

        """
        pass


class SerializerUserTestCase(TestCase):
    """
    Тестирование сериалайзера на использование.
    Когда пишим тесты, достаточно наследоваться от класса,
    Определить атрибут serializer_class,
    Реализовать методы: create_params.

    """
    serializer_class = SerializerPrimitiveField
    fullness_types = ('empty', 'middle', 'full', 'validation_error')
    # TODO: Додумать что делать с дефолтными значеними.

    def __create_object(self, data):
        """
        Рекурсивное создание объекта из словаря.

        :param dict data: Данные, которые прератяться в в атрибуты объекта.

        :return: Созданный объект.
        :rtype: object

        """
        return type('object', (object,), {
            key: self.__create_object(val) if isinstance(val, collections.Mapping) else val
            for key, val in data.items()
        })

    def __create_params(self, fullness=None):
        """
        Создаем данные для сериалайзера. Внутренний метод, прослойка перед пользовательским.

        :param str fullness: Тип создания данных: `empty`, `middle`, `full`, `validation_error`.

        :return: Словарь с данными.
        :rtype: dict

        """
        if fullness not in self.fullness_types:
            self.fail('Тип генерируемых данных должен быть одним из `{}`, пришло `{}`.'.format(
                self.fullness_types, fullness
            ))
        return self.create_params(fullness)

    def create_params(self, fullness):
        """
        Создаем данные для сериалайзера.

        :param str fullness: Тип создания данных: `empty`, `middle`, `full`, `validation_error`.

        :return: Словарь с данными.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True}
        elif fullness == 'validation_error':
            return {}
        else:
            return {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}

    def test_data_serializer(self):
        """
        Тестирование data атрибута для сериалайзера.

        """
        # Сначала скармливаем ему пустые данные.
        ser = self.serializer_class(data=self.__create_params(fullness='empty'))
        assert ser.is_valid() is False, '`.is_valid()` должен вернуть False.'
        assert isinstance(ser.errors, collections.Mapping), '`.errors` должен быть словарем.'
        assert len(ser.errors) > 0, '`.errors` должен содержать ошибки.'
        assert isinstance(ser.validated_data, collections.Mapping), '`.validated_data` должен быть словарем.'
        assert len(ser.validated_data) == 0, '`.validated_data` должен быть пустым.'

        # Проверяем что исключение выбрасывается в случае ошибок.
        ser = self.serializer_class(data=self.__create_params(fullness='validation_error'))
        try:
            ser.is_valid(raise_exception=True)
            self.fail('`.is_valid(raise_exception=True)` должен выбросить исключение `ValidationError`.')
        except ValidationError:
            pass

        # Теперь скармливаем данные частично.
        ser = self.serializer_class(data=self.__create_params(fullness='middle'))
        assert ser.is_valid() is False, '`.is_valid()` должен вернуть False.'
        assert isinstance(ser.errors, collections.Mapping), '`.errors` должен быть словарем.'
        assert len(ser.errors) > 0, '`.errors` должен содержать ошибки.'
        assert isinstance(ser.validated_data, collections.Mapping), '`.validated_data` должен быть словарем.'
        assert len(ser.validated_data) == 0, '`.validated_data` должен быть пустым.'

        # Теперь скармливаем данные полностью.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(data=data)
        # Проверяем логику.
        assert ser.is_valid() is True, '`.is_valid()` должен вернуть True.'
        assert isinstance(ser.errors, collections.Mapping), '`.errors` должен быть словарем.'
        assert len(ser.errors) == 0, '`.errors` должен быть пустым.'
        assert isinstance(ser.validated_data, collections.Mapping), '`.validated_data` должен быть словарем.'
        assert len(ser.validated_data) > 0, '`.validated_data` должен содержать данные.'
        # Проверяем, что все данные вернулись верно.
        for k, v in ser.validated_data.items():
            if k in data:
                assert v == data[k]
                del data[k]
        assert len(data) == 0, 'Все данные в `.validated_data` должны совпадать с данными в `data`.'

    def testinstance_object_serializer(self):
        """
        Тестирование instance атрибута для сериалайзера.
        Скармливаем объект.

        """
        # Сначала скармливаем ему пустой объект.
        ser = self.serializer_class(instance=self.__create_object(self.__create_params(fullness='empty')))
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'

        # Теперь скармливаем данные частично.
        data = self.__create_params(fullness='middle')
        ser = self.serializer_class(instance=self.__create_object(data))
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'
        for k, v in ser.data.items():
            if k in data:
                assert v == data[k], 'Атрибут `{}` объекта должен быть `{}`, он `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'Размер данных должен совпадать с исходным. Осталось: {}.'.format(data)

        # Теперь скармливаем данные полностью.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(instance=self.__create_object(data))
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'
        for k, v in ser.data.items():
            if k in data:
                assert v == data[k], 'Атрибут `{}` объекта должен быть `{}`, он `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'Размер данных должен совпадать с исходным. Осталось: {}.'.format(data)

    def testinstance_dict_serializer(self):
        """
        Тестирование instance атрибута для сериалайзера с примитивами.
        Скармливаем словарь.

        """
        # Сначала скармливаем ему пустой объект.
        ser = self.serializer_class(instance=self.__create_params(fullness='empty'))
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'

        # Теперь скармливаем данные частично.
        data = self.__create_params(fullness='middle')
        ser = self.serializer_class(instance=data)
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'
        for k, v in ser.data.items():
            if k in data:
                assert v == data[k], 'Атрибут `{}` объекта должен быть `{}`, он `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'Размер данных должен совпадать с исходным. Осталось: {}.'.format(data)

        # Теперь скармливаем данные полностью.
        data = self.__create_params(fullness='full')
        ser = self.serializer_class(instance=data)
        assert isinstance(ser.data, collections.Mapping), '`.data` должен быть словарем.'
        for k, v in ser.data.items():
            if k in data:
                assert v == data[k], 'Атрибут `{}` объекта должен быть `{}`, он `{}`.'.format(k, v, data[k])
                del data[k]
        assert len(data) == 0, 'Размер данных должен совпадать с исходным. Осталось: {}.'.format(data)


class SerializerSingleMixinTestCase(SerializerUserTestCase):
    """
    Тестирование сериалайзера с вложенным сериалайзером одного объекта.

    """
    serializer_class = SerializerMixinSingle

    def create_params(self, fullness):
        """
        Создаем данные для сериалайзера.

        :param str fullness: Тип создания данных: `empty`, `middle`, `full`, `validation_error`.

        :return: Словарь с данными.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': {'integer_f': 123, 'bool_f': True}}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}
            }


class SerializerManyMixinTestCase(SerializerUserTestCase):
    """
    Тестирование сериалайзера с вложенным сериалайзером с множеством объектов.

    """
    serializer_class = SerializerMixinMany

    def create_params(self, fullness):
        """
        Создаем данные для сериалайзера.

        :param str fullness: Тип создания данных: `empty`, `middle`, `full`, `validation_error`.

        :return: Словарь с данными.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': [{'integer_f': 123, 'bool_f': True}]}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': [{'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}]
            }


class SerializerRequiredMixinTestCase(SerializerUserTestCase):
    """
    Тестирование сериалайзера с вложенным обязательным сериалайзером.

    """
    serializer_class = SerializerMixinRequired

    def create_params(self, fullness):
        """
        Создаем данные для сериалайзера.

        :param str fullness: Тип создания данных: `empty`, `middle`, `full`, `validation_error`.

        :return: Словарь с данными.
        :rtype: dict

        """
        if fullness == 'empty':
            return {}
        elif fullness == 'middle':
            return {'char_f': 'qwe', 'ser_f': {'integer_f': 123, 'bool_f': True}}
        elif fullness == 'validation_error':
            return {}
        else:
            return {
                'char_f': 'rty',
                'ser_f': {'char_f': 'qwe', 'integer_f': 123, 'bool_f': True, 'float_f': 1.0, 'list_f': ['123', '123']}
            }
