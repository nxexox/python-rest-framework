"""
Utilities for working with raw html request body.

"""
import re

from rest_framework.utils.collections import MultiValueDict


def is_html_input(dictionary):
    """
    We check that it came html form or JSON request.

    :param object dictionary: Object with dictionary interface.

    :return: Check result.
    :rtype: bool

    """
    return hasattr(dictionary, 'getlist')


def parse_html_list(dictionary, prefix=''):
    """
    Parsing html form, and we get sheets and dicts.

    * List example.
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

    * Dict example.
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

    # We run on the values.
    for field, value in dictionary.items():
        # Parsing for the presence of keys with [].
        match = regex.match(field)
        if not match:
            continue

        # Try to understand, it is an array index or a dict key.
        index, key = match.groups()
        index = int(index)

        if not key:
            # If list.
            ret[index] = value
        elif isinstance(ret.get(index), dict):
            # If dict.
            ret[index][key] = value
        else:
            # Else save source string.
            ret[index] = MultiValueDict({key: [value]})

    # Return result.
    return [ret[item] for item in sorted(ret.keys())]
