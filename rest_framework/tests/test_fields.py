"""
Тестирование филдов.

"""
from unittest import TestCase

import six

from rest_framework.exceptions import ValidationError, SkipError
from rest_framework.serializers.fields import (
    Field, CharField, IntegerField, FloatField, BooleanField, ListField,
    get_attribute
)
from rest_framework.serializers.validators import (
    RequiredValidator, MaxValueValidator, MinValueValidator, MinLengthValidator, MaxLengthValidator
)


class BaseFieldTestCase(TestCase):
    """
    Тестирование базового класса филда.

    """
    field_class = Field
    abstract_methods = {
        'to_internal_value': {'data': None},
        'to_representation': {'value': None},
    }  # Пользовательские абтсрактные методы.
    requirement_arguments_for_field = {}  # Обязательные аргументы для создания филда.

    to_representation_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        # data - вход, return - выход, params - вход __init__, exceptions - ожидаемые ошибки
        # {'data': {}, 'return': None, 'params': {}, 'exceptions': []}
        {},
    )  # Кейсы для проверки работоспособности run_validation.

    field_error_messages = {}  # Пользовательский список ключей ошибок у филда.

    _fields_vals = {
        'required': True, 'default': None, 'label': None, 'validators': [],
        'error_messages': {}, 'default_error_messages': {}, 'default_validators': []
    }
    __error_messages = {'required': None, 'null': None}  # Дефолтный список ошибок.

    # Класс для тестирования на пустоту.
    class Empty:
        pass

    @classmethod
    def setUpClass(cls):
        """
        Дополняем данные для каждого поля отдельно.

        """
        cls.__error_messages.update(cls.field_error_messages)

    def assert_base_fields(self, field, **additional_fields):
        """
        Проверяет на все базовые филды и на дополнительные.

        :param rest_framework.serializers.fields.Field field: Объект филда.
        :param additional_fields: Словарь дополнительных филдов для проверки.

        """
        copy_fields = self._fields_vals.copy()
        copy_fields.update(additional_fields)
        msg = 'Неверное значение в %s у поля: {}. Ожидалось: {}, Пришло: {}.' % field.__class__.__name__

        for key, val in copy_fields.items():
            field_val = getattr(field, key, self.Empty())
            # Пробуем проверить тремя способами в зависимости от типа.
            if isinstance(val, (bool, type(None))):  # Сначала сингл типы.
                assert val is field_val, msg.format(key, val, field_val)
            elif isinstance(val, (six.string_types + six.integer_types + (float,))):  # Теперь примитивы.
                assert val == field_val, msg.format(key, val, field_val)
            else:  # Если объект сложный.
                assert isinstance(val, type(field_val)), msg.format(key, val, type(field_val))

    def create_params(self, **params):
        """
        Создание параметров, для создания объекта филда.

        :return: Параметры для создания филда.
        :rtype: dict

        """
        r_params = self.requirement_arguments_for_field.copy()
        r_params.update(params)
        return r_params

    def assert_bind(self, field, field_name=None, parent=None, label=None):
        """
        Проверяет последствия действия метода bind.

        :param rest_framework.serializers.fields.Field field: Объект который проверяем.
        :param str field_name: Название филда.
        :param object parent: Родительский филд.
        :param str label: Label филда.

        """
        assert field.label == label, '`.label` должен быть {}, а пришло {}.'.format(label, field.label)
        assert field.parent == parent, '`.parent` должен быть {},  а пришло {}.'.format(parent, field.parent)
        assert field.field_name == field_name, \
            '`.field_name` должен быть {}, а пришло {}.'.format(field_name, field.field_name)

    def create_method_for_get_attribute(self, field_name=None, call_bind=True,
                                        default=None, required=None, attr=None, set_self=True, **kwargs):
        """
        Создание атрибута у объекта, что бы протестировать `field.get_attribute()`

        :param str field_name: Название филда.
        :param bool call_bind: Нужно ли вызывать bind метод у филда?
        :param object default: Значение по умолчанию.
        :param bool required: Обязательно ли поле.
        :param object attr: Сам стрибут, который ставим.
        :param bool set_self: Нужно ли устанавливать ссылку классу родителю.

        :return: Созданный и готовый к тестированию Field.
        :rtype: rest_framework.serializers.fields.Field

        """
        field = self.field_class(**self.create_params(required=required, default=default, **kwargs))
        if call_bind:
            field.bind(field_name, self)
        if set_self:
            setattr(self, field_name, attr)
        return field

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

                data = data or {}  # Превращаем None в словарь.

                # Строим филд и ищем метод для тестирования.
                field = self.field_class(**self.create_params(**params))
                method = getattr(field, method_name, self.Empty())
                if isinstance(method, self.Empty):
                    self.fail('Тестирование по кейсам не удалось. Не удалось найти метод `{}` у класса `{}`.'.format(
                        method_name, field.__class__.__name__
                    ))

                # Если ожидаются ошибки.
                if exceptions:
                    try:
                        res = method(**data)
                        self.fail('В методе `{}.{}()` кейс `{}` не выкинул исключение. Метод вернул: `{}`.'.format(
                            field.__class__.__name__, method_name, case, res
                        ))
                    except tuple(exceptions):
                        pass
                else:
                    # Если ошибок не ожидается.
                    res = method(**data)
                    assert res == result, \
                        'В методе `{}.{}()` кейс {} вернул неверный результат `{}`'.format(
                            field.__class__.__name__, method_name, case, res
                        )
            except Exception as e:
                self.fail('Во время проверки кейса `{}` для метода `{}.{}` произошла неожиданная ошибка: `{}: {}`'.format(
                    case, self.field_class.__class__.__name__, method_name, e.__class__.__name__, e
                ))

    def test_default_create(self):
        """
        Тестирование создания c дефолтными настройками.

        """
        self.assert_base_fields(self.field_class(**self.create_params()))  # Сначала создание с дефолтными.

        # Теперь создание с настройками.
        params = self.create_params(required=False)
        self.assert_base_fields(self.field_class(**params), **params)

        # Смотрим как default влияет на required.
        params = self.create_params(default='')
        self.assert_base_fields(self.field_class(**params), required=False, **params)

        # Смотрим как required влияет на validators.
        field = self.field_class(**self.create_params(required=True))
        assert isinstance(field.validators, list), \
            '`.validators` должен быть list, а пришло {}'.format(type(field.validators))
        assert len(field.validators) == 1, \
            'В `.validators` должен быть 1 валидатор, а их {}'.format(len(field.validators))
        assert isinstance(field.validators[0], RequiredValidator), \
            'В `.validators` должен быть `RequiredValidator`. Пришло: {}'.format(type(field.validators[0]))
        # Теперь проверяем, что валидатора нет.
        field = self.field_class(**self.create_params(required=False))
        assert isinstance(field.validators, list), \
            '`.validators` должен быть list, а пришло {}'.format(type(field.validators))
        assert len(field.validators) == 0, \
            'В `.validators` не должно быть валидаторов, а их {}'.format(len(field.validators))

        # Проверяем собщения об ошибке.
        field, messages_keys = self.field_class(**self.create_params()), self.__error_messages
        for key in field.error_messages:
            assert key in messages_keys, 'В `.error_messages` должен быть ключ {}.'.format(key)

        # Обновляем словарь ошибок, и пробуем с кастомной ошибкой.
        new_error_message = self.__error_messages.copy()
        new_error_message['test'] = None
        field = self.field_class(**self.create_params(error_messages={'test': 'test'}))
        messages_keys = new_error_message

        for key in field.error_messages:
            assert key in messages_keys, 'В `.error_messages` должен быть ключ {}.'.format(key)

    def test_bind(self):
        """
        Тестирование bind метода.

        """
        # Сначала дефолтные.
        field = self.field_class(**self.create_params())
        field.bind('test_label', self)
        self.assert_bind(field, 'test_label', self, 'Test label')

        # Теперь ставим label.
        field = self.field_class(**self.create_params(label='test_label'))
        field.bind('test_label', self)
        self.assert_bind(field, 'test_label', self, 'test_label')

    def test_fail(self):
        """
        Тестирование метода fail.

        """
        # Тестируем без своих ошибок.
        field = self.field_class(**self.create_params())
        try:
            field.fail('required')
            self.fail('`.fail()` должен выбрасывать исключение `ValidationError`.')
        except ValidationError:
            pass
        try:
            field.fail('test')
            self.fail('`.fail()` должен выбрасывать исключение `AssertionError`.')
        except AssertionError:
            pass

        # Теперь добавляем свое сообщение об ошибке.
        field = self.field_class(**self.create_params(error_messages={'test': '{test}-test'}))
        try:
            field.fail('test', test='test')
            self.fail('`.fail()` должен выбрасывать исключение `ValidationError`.')
        except ValidationError as e:
            assert e.detail == 'test-test', 'Сообщение об ошибке должно быть `{}`, пришло `{}`.'.format(
                'test-test', e.detail
            )

    def test_abstract_methods(self):
        """
        Тестирование абстрактных методов.

        """
        field = self.field_class(**self.create_params())
        for method_name, method_params in self.abstract_methods.items():
            try:
                getattr(field, method_name, lambda: None)(**method_params)
                self.fail('Метод `.{}` должен выбрасывать исключение `NotImplementedError`.'.format(method_name))
            except NotImplementedError:
                pass

    def test_to_internal_value(self):
        """
        Тест преобразования данных в валидный питон объект.

        """
        if 'to_internal_value' not in self.abstract_methods:
            self.__test_method_cases('to_internal_value')

    def test_to_representation(self):
        """
        Тест преобразования данных в валидный JSON объект.

        """
        if 'to_representation' not in self.abstract_methods:
            self.__test_method_cases('to_representation')

    def test_get_default(self):
        """
        Тестирование get_default метода.

        """
        field = self.field_class(**self.create_params())
        res = field.get_default()
        assert res is None, '`.get_default()` должен возвращать None, вернул: {}.'.format(res)

        field = self.field_class(**self.create_params(default=1))
        res = field.get_default()
        assert res == 1, '`.get_default()` должен возвращать 1, вернул: {}.'.format(res)

        field = self.field_class(**self.create_params(default=lambda: 100))
        res = field.get_default()
        assert res == 100, '`.get_default()` должен вернуть 100, вернул: {}.'.format(res)

    def test_get_attribute(self):
        """
        Тестирование метода get_attribute.

        """
        params = dict(
            field_name='test_get_attribute_field', call_bind=True, required=False, default=None,
            attr=self.test_get_attribute, set_self=True
        )

        # Сначала нормальную работу.
        res = self.create_method_for_get_attribute(**params).get_attribute(self)
        assert res == self.test_get_attribute, \
            '`.get_attribute()` должен возвращать {}, вернул {}.'.format(self.test_get_attribute, res)

        # Теперь пробуем несуществующий поискать и вернуть default.
        params.update(default=100, call_bind=False, attr=None, set_self=False)
        res = self.create_method_for_get_attribute(**params).get_attribute(self)
        assert res == 100, '`.get_attribute()` должен возвращать 100, вернул {}.'.format(res)

        # Смотрим, что если поле обязательное и нет default, кидает исключение `SkipError`.
        params.update(required=True, default=None)
        try:
            self.create_method_for_get_attribute(**params).get_attribute(self)
            self.fail('`.get_attribute()` должен выбросить исключение `SkipError`.')
        except SkipError:
            pass

        # Теперь пробуем оригинальное исключение получить.
        params.update(field_name=None, required=False, call_bind=True)
        try:
            res = self.create_method_for_get_attribute(label='test', **params).get_attribute(self)
            self.fail('`.get_attribute()` должен выбросить исключение `TypeError`, а вернул `{}`.'.format(res))
        except TypeError:
            pass
        except Exception as e:
            self.fail('`.get_attribute()` должен выбросить исключение `TypeError`, а выбросил {}.'.format(type(e)))

    def test_validate_empty_values(self):
        """
        Тестирование валидации на пустой тип.

        """
        # Сначала с дефолтными настройками.
        field = self.field_class(**self.create_params(required=False))
        is_empty, data = field.validate_empty_values(None)
        assert is_empty is True, '`.validate_empty_values()` должен вернуть True.'
        assert data is None, '`.validate_empty_values()` должен вернуть None.'

        # Теперь проверяем рекакцию на обязательность.
        field = self.field_class(**self.create_params(required=True))
        try:
            field.validate_empty_values(None)
            self.fail('`.validate_empty_values()` должен выбросить исключение `ValidationError`.')
        except ValidationError:
            pass

        # Теперь проверяем на нормальность данных.
        field = self.field_class(**self.create_params(required=True))
        is_empty, data = field.validate_empty_values(123)
        assert is_empty is False, '`.validate_empty_values()` должен вернуть False.'
        assert data == 123, '`.validate_empty_values()` должен вернуть 123.'

    def test_run_validation(self):
        """
        Тестирование запуска валидации.

        """
        self.__test_method_cases('run_validation')

    def test_run_validation_base_field(self):
        """
        Тестирование запуска валидации для базового филда.

        """
        to_internal_value = lambda x: x  # Делаем заглушку для внутренней функции.
        # Проверяем, на дефолтных настройках.
        field = self.field_class(**self.create_params())
        setattr(field, 'to_internal_value', to_internal_value)
        res = field.run_validation(123)
        assert res == 123, '`.run_validation()` должен вернуть 123.'

        # Проверяем, когда поле обязательное.
        field = self.field_class(**self.create_params(required=True))
        setattr(field, 'to_internal_value', to_internal_value)
        res = field.run_validation(123)
        assert res == 123, '`.run_validation()` должен вернуть 123.'

        # Теперь пробуем заставить валидатор работать.
        try:
            field.run_validation(None)
            self.fail('`.run_validation()` должен выбросить исключение `ValidationError`.')
        except ValidationError:
            pass

    def test_run_validators(self):
        """
        Тестирует работы валидаторов.

        """
        # Проверяем без валидаторов.
        field = self.field_class(**self.create_params(required=False, validators=[]))
        field.run_validators(123)

        # Проверяем дефолтными валидаторами.
        field = self.field_class(**self.create_params(required=True, validators=[]))
        field.run_validators(123)
        try:
            field.run_validators(None)
            self.fail('`.run_validators()` должен выбросить исключение `ValidationError`.')
        except ValidationError:
            pass

        # Проверяем кастомными валидаторами.
        def test_validator(value):
            if value == 1:
                raise ValidationError(1)

        field = self.field_class(**self.create_params(required=True, validators=[test_validator]))
        field.run_validators(10)
        try:
            field.run_validators(1)
            self.fail('`.run_validators()` должен выбросить исключение `ValidationError`.')
        except ValidationError:
            pass


class CharFieldTest(BaseFieldTestCase):
    """
    Тестирование CharField.

    """
    field_class = CharField
    abstract_methods = {}  # Пользовательские абтсрактные методы.
    field_error_messages = {
        'invalid': None,
        'blank': None,
        'min_length': None,
        'max_length': None
    }  # Пользовательский список ошибок.
    to_representation_cases = (
        {'data': {'value': '123'}, 'return': '123'},
        {'data': {'value': 123}, 'return': '123'},
        {'data': {'value': 'qwe'}, 'return': 'qwe'}
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        {'data': {'data': '123'}, 'return': '123'},
        {'data': {'data': True}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)}
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        {'data': {'data': '123'}, 'return': '123'},
        {'data': {'data': 123}, 'return': '123'},
        {'data': {'data': 'qwe'}, 'return': 'qwe'},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'params': {'required': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ''}, 'params': {'allow_blank': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ''}, 'params': {'allow_blank': True}, 'return': ''},
        {'data': {'data': '   '}, 'params': {'allow_blank': True, 'trim_whitespace': True}, 'return': ''},
        {'data': {'data': '   '}, 'params': {'allow_blank': False, 'trim_whitespace': True}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности run_validation.

    def test_init(self):
        """
        Тестирование создания.

        """
        params = dict(max_length=10, min_length=20, trim_whitespace=False, allow_blank=True, required=True)
        field = self.field_class(**params)

        # Смотрим на валидаторы.
        assert len(field.validators) == 3, '`.validators` должен иметь длину 3, он {}'.format(len(field.validators))
        for v in field.validators:
            assert isinstance(v, (RequiredValidator, MaxLengthValidator, MinLengthValidator)), \
                'Валидатор должен быть `RequiredValidator, MaxLengthValidator, MinLengthValidator`, он `{}`'.format(
                    type(v)
                )

        # Смотрим, что без них тоже можно.
        params.update(max_length=None, min_length=None)
        field = self.field_class(**params)
        assert len(field.validators) == 1, '`.validators` должен иметь длину 1, он {}'.format(len(field.validators))
        for v in field.validators:
            assert isinstance(v, RequiredValidator), 'Валидатор должен быть `RequiredValidator`, он `{}`'.format(type(v))


class TestIntegerField(BaseFieldTestCase):
    """
    Тестирование IntegerField.

    """
    field_class = IntegerField
    abstract_methods = {}  # Пользовательские абтсрактные методы.
    field_error_messages = {
        'invalid': None,
        'min_value': None,
        'max_value': None,
        'max_string_length': None
    }  # Пользовательский список ошибок.
    to_representation_cases = (
        {'data': {'value': 123}, 'return': 123},
        {'data': {'value': '123'}, 'return': 123},
        {'data': {'value': 'qwe'}, 'exceptions': (ValueError,)},
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': '123.0'}, 'return': 123},
        {'data': {'data': '123.1'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        {'data': {'data': 123}, 'return': 123},
        {'data': {'data': '123'}, 'return': 123},
        {'data': {'data': '123.0'}, 'return': 123},
        {'data': {'data': '123.1'}, 'exceptions': (ValidationError,)},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'min_value': 5}, 'return': 10},
        {'data': {'data': 10}, 'params': {'min_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'min_value': 11}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11, 'min_value': 5}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 10, 'min_value': 10}, 'return': 10},
        {'data': {'data': 10}, 'params': {'max_value': 5, 'min_value': 5}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности run_validation.


class TestFloatField(BaseFieldTestCase):
    """
    Тестирование FloatField.

    """
    field_class = FloatField
    abstract_methods = {}  # Пользовательские абтсрактные методы.
    field_error_messages = {
        'invalid': None,
        'min_value': None,
        'max_value': None,
        'max_string_length': None
    }  # Пользовательский список ошибок.
    to_representation_cases = (
        {'data': {'value': 123}, 'return': 123.0},
        {'data': {'value': '123'}, 'return': 123.0},
        {'data': {'value': 'qwe'}, 'exceptions': (ValueError,)},
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        {'data': {'data': 123}, 'return': 123.0},
        {'data': {'data': '123'}, 'return': 123.0},
        {'data': {'data': '123.0'}, 'return': 123.0},
        {'data': {'data': '123.1'}, 'return': 123.1},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'return': 0.0},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        {'data': {'data': 123}, 'return': 123.0},
        {'data': {'data': '123'}, 'return': 123.0},
        {'data': {'data': '123.0'}, 'return': 123.0},
        {'data': {'data': '123.1'}, 'return': 123.1},
        {'data': {'data': 'qwe'}, 'exceptions': (ValidationError,)},
        {'data': {'data': False}, 'return': 0.0},
        {'data': {'data': '11' * IntegerField.MAX_STRING_LENGTH}, 'exceptions': (ValidationError,)},
        {'data': {'data': None}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'min_value': 5}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'min_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'min_value': 11}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': 10}, 'params': {'max_value': 11, 'min_value': 5}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 10, 'min_value': 10}, 'return': 10.0},
        {'data': {'data': 10}, 'params': {'max_value': 5, 'min_value': 5}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности run_validation.


class TestBooleanField(BaseFieldTestCase):
    """
    Тестирование BooleanField.

    """
    field_class = BooleanField
    abstract_methods = {}  # Пользовательские абтсрактные методы.
    field_error_messages = {'invalid': None}
    to_representation_cases = (
        {'data': {'value': True}, 'return': True},
        {'data': {'value': False}, 'return': False},
        {'data': {'value': None}, 'return': None},
        {'data': {'value': 'Yes'}, 'return': True},
        {'data': {'value': 1}, 'return': True},
        {'data': {'value': 'No'}, 'return': False},
        {'data': {'value': 0}, 'return': False},
        {'data': {'value': 'null'}, 'return': None},
        {'data': {'value': ''}, 'return': None},
        {'data': {'value': '100'}, 'return': True}
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        {'data': {'data': True}, 'return': True},
        {'data': {'data': False}, 'return': False},
        {'data': {'data': None}, 'return': None},
        {'data': {'data': 'Yes'}, 'return': True},
        {'data': {'data': 1}, 'return': True},
        {'data': {'data': 'No'}, 'return': False},
        {'data': {'data': 0}, 'return': False},
        {'data': {'data': 'null'}, 'return': None},
        {'data': {'data': ''}, 'return': None},
        {'data': {'data': '100'}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        {'data': {'data': True}, 'return': True},
        {'data': {'data': False}, 'return': False},
        {'data': {'data': None}, 'params': {'required': False}, 'return': None},
        {'data': {'data': 'Yes'}, 'return': True},
        {'data': {'data': 1}, 'return': True},
        {'data': {'data': 'No'}, 'return': False},
        {'data': {'data': 0}, 'return': False},
        {'data': {'data': 'null'}, 'params': {'required': False}, 'return': None},
        {'data': {'data': ''}, 'params': {'required': False}, 'return': None},
        {'data': {'data': '100'}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности run_validation.


class TestListField(BaseFieldTestCase):
    """
    Тестирование ListField.

    """
    field_class = ListField
    abstract_methods = {}  # Пользовательские абтсрактные методы.
    requirement_arguments_for_field = {
        'child': CharField(required=False)
    }  # Обязательные аргументы для создания филда.
    field_error_messages = {
        'not_a_list': None,
        'empty': None,
        'min_length': None,
        'max_length': None
    }
    _fields_vals = {
        'required': True, 'default': None, 'label': None, 'validators': [],
        'error_messages': {}, 'default_error_messages': {}, 'default_validators': [],
        'child': CharField()
    }

    to_representation_cases = (
        {'data': {'value': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'value': [123, 123, 123]}, 'return': ['123', '123', '123']},
        {'data': {'value': [True, True, True]}, 'return': ['True', 'True', 'True']},
        {'data': {'value': ['123', 123, True, None]}, 'return': ['123', '123', 'True', None]},
        {'data': {'value': None}, 'exceptions': (TypeError,)},
    )  # Кейсы, для проверки работоспособности representation.
    to_internal_value_cases = (
        {'data': {'data': ''}, 'exceptions': (ValidationError,)},
        {'data': {'data': {}}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': []}, 'params': {'allow_empty': True}, 'return': []},
        {'data': {'data': []}, 'params': {'allow_empty': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'data': [123, 123, 123]}, 'return': ['123', '123', '123']},
        # Ошибки тут будут, потому что CharField не хавает True False None в качестве строки.
        {'data': {'data': [True, True, True]}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', 123, True, None]}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности to_internal.
    run_validation_cases = (
        {'data': {'data': ''}, 'exceptions': (ValidationError,)},
        {'data': {'data': {}}, 'exceptions': (ValidationError,)},
        {'data': {'data': BaseFieldTestCase.Empty()}, 'exceptions': (ValidationError,)},
        {'data': {'data': []}, 'params': {'allow_empty': True}, 'return': []},
        {'data': {'data': []}, 'params': {'allow_empty': False}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', '123', '123']}, 'return': ['123', '123', '123']},
        {'data': {'data': [123, 123, 123]}, 'return': ['123', '123', '123']},
        # Ошибки тут будут, потому что CharField не хавает True False None в качестве строки.
        {'data': {'data': [True, True, True]}, 'exceptions': (ValidationError,)},
        {'data': {'data': ['123', 123, True, None]}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 2, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 5}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'max_length': 2}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 5, 'max_length': 10}, 'exceptions': (ValidationError,)},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 3, 'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 5, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 3, 'child': IntegerField()}, 'return': [1, 1, 1]},
        {'data': {'data': [1, 1, 1]}, 'params': {'min_length': 1, 'max_length': 2}, 'exceptions': (ValidationError,)},
    )  # Кейсы для проверки работоспособности run_validation.
