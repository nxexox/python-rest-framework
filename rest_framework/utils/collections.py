"""
Коллекции.

"""
import copy

import six


class MultiValueDictKeyError(KeyError):
    """
    Кастомный KeyError.

    """
    pass


class MultiValueDict(dict):
    """
    Словарь, позволяющий хранить множество значений в одном ключе.
    Сделали что бы решить проблему cgi.parse_qs,
    которая возвращает список для каждого ключа, хотя в большинстве веб формы дают пары ключ значение.


    >>> d = MultiValueDict({'name': ['Adrian', 'Simon'], 'position': ['Developer']})
    >>> d['name']
    'Simon'
    >>> d.getlist('name')
    ['Adrian', 'Simon']
    >>> d.getlist('doesnotexist')
    []
    >>> d.getlist('doesnotexist', ['Adrian', 'Simon'])
    ['Adrian', 'Simon']
    >>> d.get('lastname', 'nonexistent')
    'nonexistent'
    >>> d.setlist('lastname', ['Holovaty', 'Willison'])
    """
    def __init__(self, key_to_list_mapping=()):
        """
        Словарь, позволяющий хранить множество значений в одном ключе.
        Сделали что бы решить проблему cgi.parse_qs,
        которая возвращает список для каждого ключа, хотя в большинстве веб формы дают пары ключ значение.

        :param iter key_to_list_mapping: Данные для инициализации.

        """
        super(MultiValueDict, self).__init__(key_to_list_mapping)

    def __getitem__(self, key):
        """
        Возвращает последнее значение для этого ключа или [] если это пустой список.
        Если не найдено кидаем ошибку.

        :param object key: Ключ, по которому ищем.

        :return: Найденое значение.
        :rtype: object

        :raise KeyError: Если не нашли ключ.

        """
        # Сначала ищем в словаре массив.
        try:
            list_ = super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            raise MultiValueDictKeyError(repr(key))
        # Теперь берем последнее значение.
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        """
        Ставим в качестве значения массив.

        :param object key: Ключ, ко которому ставим.
        :param object value: Значение которое ставим.

        """
        super(MultiValueDict, self).__setitem__(key, [value])

    def __copy__(self):
        """
        Делаем копирование словаря. ак же копируем все значения, т.к. они массивы.

        :return: Скопированный словарь.
        :rtype: MultiValueDict

        """
        return self.__class__([
            (k, v[:])
            for k, v in self.lists()
        ])

    def __deepcopy__(self, memo=None):
        """
        Делаем глубокое копирование всего словаря.

        :param memo: ???

        :return: Скопированный словарь.
        :rtype: MultiValueDict

        """
        if memo is None:
            memo = {}

        result = self.__class__()
        memo[id(self)] = result

        for key, value in dict.items(self):
            dict.__setitem__(result, copy.deepcopy(key, memo), copy.deepcopy(value, memo))

        return result

    def __getstate__(self):
        """
        Делаем свое состояние для пикла объекта.

        :return: Сохраняем в _data данные для setstate.
        :rtype: MultiValueDict

        """
        obj_dict = self.__dict__.copy()
        obj_dict['_data'] = {k: self._getlist(k) for k in self}
        return obj_dict

    def __setstate__(self, obj_dict):
        """
        Развораяиваем что запикали в dict.

        :param dict obj_dict: Данные которые надо развернуть.

        :return: Развернутые и преобразованные данные.
        :rtype: MultiValueDict

        """
        data = obj_dict.pop('_data', {})
        for k, v in data.items():
            self.setlist(k, v)
        self.__dict__.update(obj_dict)

    def get(self, key, default=None):
        """
        Возврвщаем последнее значение из найденных.
        Если ничего не нашли, или значение по ключу пусто, возвращаем `default=`.

        """
        # Ищем по ключу.
        try:
            val = self[key]
        except KeyError:
            return default
        # Возвращаем что нашли.
        if val == []:
            return default
        return val

    def _getlist(self, key, default=None, force_list=False):
        """
        Возвращаем лист значение для ключа.

        :param object key: Ключ, по которому достаем.
        :param object default: Дефолтное значение.
        :param bool force_list: Нужно ли делать копию значения?

        :return: Список значени или `default=`.
        :rtype: list

        """
        try:
            # Достаем по ключу.
            values = super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            # Если не нашли.
            if default is None:
                return []
            return default
        else:
            # Если нашли, то возвращаем. Если надо делаем копию.
            if force_list:
                values = list(values) if values is not None else None
            return values

    def getlist(self, key, default=None):
        """
        Возвращает список значений по ключу. Если ключ не найден, возвращает `default=`.

        :param object key: Ключ, по которому ищем.
        :param object default: Дефолтное значение.

        :return: Список значений.
        :rtype: list

        """
        return self._getlist(key, default, force_list=True)

    def setlist(self, key, list_):
        """
        Устанавливаем массив значений по ключу.

        :param object key: Ключ, по котормоу ставим.
        :param list list_: Список значений, которые ставим.

        """
        super(MultiValueDict, self).__setitem__(key, list_)

    def setdefault(self, key, default=None):
        """
        Возвращаем значение по ключу, если не нашли тогда ставим `default=` и возвращаем его.

        :param object key: Ключ, по которому возвращаем.
        :param object default: Дефолтное значение, которое стоит установить.

        :return: Значение по ключу.
        :rtype: object

        """
        if key not in self:
            self[key] = default
        return self[key]

    def setlistdefault(self, key, default_list=None):
        """
        Возвращаем список значений по ключу, если не нашли ставим `default_list=`.

        :param object key: Ключ, по которому ставим.
        :param list default_list: Список значений по умолчанию.

        :return: Значение по ключу.
        :rtype: list

        """
        if key not in self:
            if default_list is None:
                default_list = []
            self.setlist(key, default_list)

        return self._getlist(key)

    def appendlist(self, key, value):
        """
        Добавляем значение в список, найденный по ключу.

        :param object key: Ключ, по которому ищем.
        :param object value: Значение, которое стоит добавить.

        """
        self.setlistdefault(key).append(value)

    def items(self):
        """
        Генератор по значениям словаря.

        :return: Генератор по словарю. tuple(key, value)
        :rtype: Generator[Tuple[object, object], None, None]

        """
        for key in self:
            yield key, self[key]

    def lists(self):
        """
        Генератор по словарю. В качестве значения список значений по ключу.

        :return: Генератор по словарю. tuple(key, value)
        :rtype: Generator[Tuple[object, list], None, None]

        """
        return six.iteritems(super(MultiValueDict, self))

    def values(self):
        """
        Генератор по значениям. Возвращает последнее найденное значение.

        :return: Последнее найденное в списке по ключу значение.
        :rtype: object

        """
        for key in self:
            yield self[key]

    def copy(self):
        """
        Делаем поверхностную копию объекта.

        :return: Копия словаря.
        :rtype: MultiValueDict

        """
        return copy.copy(self)

    def update(self, *args, **kwargs):
        """
        Расширяет текущий словарь, данными. Не заменяем значения по одному ключу, а дополняем их.

        """
        # Мы не можем принять несколько словарей как позиционные аргументы.
        if len(args) > 1:
            raise TypeError("Ожидался один позиционный аргумент, получено `%d`" % len(args))

        if args:
            other_dict = args[0]
            # Если это тоже словарь массивов.
            if isinstance(other_dict, MultiValueDict):
                for key, value_list in other_dict.lists():
                    self.setlistdefault(key).extend(value_list)
            else:
                # Если это простой словарь.
                try:
                    for key, value in other_dict.items():
                        self.setlistdefault(key).append(value)
                except TypeError:
                    raise ValueError("`MultiValueDict.update()` принимает либо `MultiValueDict` либо `dict`")

        # Дополняем позиционными аршументами.
        for key, value in six.iteritems(kwargs):
            self.setlistdefault(key).append(value)

    def dict(self):
        """
        Возвращаем простой словарь со списками значений.

        :return: Простой словарь.
        :rtype: dict

        """
        return {key: self[key] for key in self}
