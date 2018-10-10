"""
Утилитки, для работы с сырым html телом запроса.

"""
import re

from rest_framework.utils.collections import MultiValueDict


def is_html_input(dictionary):
    """
    Проверяем, это пришла html форма или JSON запрос.

    :param object dictionary: Объект, с интерфейсом словаря.

    :return: Результат проверки.
    :rtype: bool

    """
    return hasattr(dictionary, 'getlist')


def parse_html_list(dictionary, prefix=''):
    """
    Парсим html форму, и достаем листы и словари.

    * Пример массива.
    {
        '[0]': 'abc',
        '[1]': 'def',
        '[2]': 'hij'
    }
        -->
    [
        'abc',
        'def',
        'hij'
    ]

    * Пример словаря.
    {
        '[0]foo': 'abc',
        '[0]bar': 'def',
        '[1]foo': 'hij',
        '[1]bar': 'klm',
    }
        -->
    [
        {'foo': 'abc', 'bar': 'def'},
        {'foo': 'hij', 'bar': 'klm'}
    ]
    """
    ret = {}
    regex = re.compile(r'^%s\[([0-9]+)\](.*)$' % re.escape(prefix))

    # Бежим по значениям.
    for field, value in dictionary.items():
        # Парсим на наличие ключей с [].
        match = regex.match(field)
        if not match:
            continue

        # Пробуем понять, это индекс массива или ключ словаря.
        index, key = match.groups()
        index = int(index)

        if not key:
            # Если массив.
            ret[index] = value
        elif isinstance(ret.get(index), dict):
            # Если словарь.
            ret[index][key] = value
        else:
            # Иначе созраняем исходную структуру.
            ret[index] = MultiValueDict({key: [value]})

    # Возвращаем результат.
    return [ret[item] for item in sorted(ret.keys())]
