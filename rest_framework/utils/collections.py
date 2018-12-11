"""
Collections.

"""
import copy

import six


class MultiValueDictKeyError(KeyError):
    """
    Custom KeyError.

    """
    pass


class MultiValueDict(dict):
    """
    A dictionary that allows you to store multiple values in one key.
    We’ve done to solve the cgi.parse_qs problem,
    which returns a list for each key, although most web forms give key value pairs.


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
        A dictionary that allows you to store multiple values in one key.
        We’ve done to solve the cgi.parse_qs problem,
        which returns a list for each key, although most web forms give key value pairs.

        :param iter key_to_list_mapping: Data for initializing.

        """
        super(MultiValueDict, self).__init__(key_to_list_mapping)

    def __getitem__(self, key):
        """
        Returns the last value for this key or [] if this is an empty list.
        If not found we throw an error.

        :param object key: Key for search.

        :return: Found value.
        :rtype: object

        :raise KeyError: Id If you did not find the key.

        """
        # First we look for an array in the dict.
        try:
            list_ = super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            raise MultiValueDictKeyError(repr(key))
        # Now take the last value.
        try:
            return list_[-1]
        except IndexError:
            return []

    def __setitem__(self, key, value):
        """
        Set an array as a value.

        :param object key: Key for set.
        :param object value: Value for set.

        """
        super(MultiValueDict, self).__setitem__(key, [value])

    def __copy__(self):
        """
        Make a copy of the dictionary. We also copy all the values, since they are arrays.

        :return: Copied dict.
        :rtype: MultiValueDict

        """
        return self.__class__([
            (k, v[:])
            for k, v in self.lists()
        ])

    def __deepcopy__(self, memo=None):
        """
        Make a deep copy of the entire dictionary.

        :return: Copied dict.
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
        We make our state for the pickle object.

        :return: Сохраняем в _data данные для setstate.
        :rtype: MultiValueDict

        """
        obj_dict = self.__dict__.copy()
        obj_dict['_data'] = {k: self._getlist(k) for k in self}
        return obj_dict

    def __setstate__(self, obj_dict):
        """
        Expand that pickle in dict.

        :param dict obj_dict: The data that must be deployed.

        :return: Expanded and Transformed Data.
        :rtype: MultiValueDict

        """
        data = obj_dict.pop('_data', {})
        for k, v in six.iteritems(data):
            self.setlist(k, v)
        self.__dict__.update(obj_dict)

    def get(self, key, default=None):
        """
        We return the last value found.
        If nothing is found, or the key value is empty, return `default =`.

        """
        # Search on key.
        try:
            val = self[key]
        except KeyError:
            return default
        # Return what you find.
        if val == []:
            return default
        return val

    def _getlist(self, key, default=None, force_list=False):
        """
        Return list value for key.

        :param object key: The key for which we get.
        :param object default: Default value.
        :param bool force_list: Do I need to make a copy of the value?

        :return: List values or `default=`.
        :rtype: list

        """
        try:
            # Get on the key.
            values = super(MultiValueDict, self).__getitem__(key)
        except KeyError:
            # If not found.
            if default is None:
                return []
            return default
        else:
            # If found, then return. If you need to make a copy.
            if force_list:
                values = list(values) if values is not None else None
            return values

    def getlist(self, key, default=None):
        """
        Returns a list of values by key. If the key is not found, returns `default =`.

        :param object key: Key for search.
        :param object default: Default value.

        :return: List values.
        :rtype: list

        """
        return self._getlist(key, default, force_list=True)

    def setlist(self, key, list_):
        """
        Set list values on the key.

        :param object key: Key for set.
        :param list list_: List values for set.

        """
        super(MultiValueDict, self).__setitem__(key, list_)

    def setdefault(self, key, default=None):
        """
        Return the value by key, if not found then put `default =` and return it.

        :param object key: Key for return
        :param object default: Default value to set.

        :return: Value on the key.
        :rtype: object

        """
        if key not in self:
            self[key] = default
        return self[key]

    def setlistdefault(self, key, default_list=None):
        """
        Return the list of values by key, if they are not found, put `default_list =`.

        :param object key: Key for set.
        :param list default_list: List values on default.

        :return: Value o the key.
        :rtype: list

        """
        if key not in self:
            if default_list is None:
                default_list = []
            self.setlist(key, default_list)

        return self._getlist(key)

    def appendlist(self, key, value):
        """
        Add a value to the list found by key.

        :param object key: Key for search.
        :param object value: Value for append.

        """
        self.setlistdefault(key).append(value)

    def items(self):
        """
        Generator based on dictionary values.

        :return: Generator on dict. tuple(key, value)
        :rtype: Generator[Tuple[object, object], None, None]

        """
        for key in self:
            yield key, self[key]

    def lists(self):
        """
        Dictionary Generator. As a value, a list of values by key.

        :return: Generator on dict. tuple(key, value)
        :rtype: Generator[Tuple[object, list], None, None]

        """
        return six.iteritems(super(MultiValueDict, self))

    def values(self):
        """
        Generator by values. Returns the last found value.

        :return: Last found in the list by key value.
        :rtype: object

        """
        for key in self:
            yield self[key]

    def copy(self):
        """
        Make a shallow light of the object.

        :return: Copied dict.
        :rtype: MultiValueDict

        """
        return copy.copy(self)

    def update(self, *args, **kwargs):
        """
        Extends the current dictionary data. We do not replace the values by one key, but supplement them.

        """
        # We cannot accept several dictionaries as positional arguments.
        if len(args) > 1:
            raise TypeError("Expected one positional argument, reality `%d`" % len(args))

        if args:
            other_dict = args[0]
            # If this is also a dict of arrays.
            if isinstance(other_dict, MultiValueDict):
                for key, value_list in other_dict.lists():
                    self.setlistdefault(key).extend(value_list)
            else:
                # If this is also a dict of arrays.
                try:
                    for key, value in six.iteritems(other_dict):
                        self.setlistdefault(key).append(value)
                except TypeError:
                    raise ValueError("`MultiValueDict.update ()` accepts either `MultiValueDict` or` dict`")

        # Supplement with positional documents.
        for key, value in six.iteritems(kwargs):
            self.setlistdefault(key).append(value)

    def dict(self):
        """
        We return a simple dictionary with lists of values.

        :return: Simple dict.
        :rtype: dict

        """
        return {key: self[key] for key in self}
