"""
Helpers for serializers and fields.

"""
from collections import OrderedDict, MutableMapping


def get_class_name(obj):
    """
    Get class name attribute.

    :param Any obj: Object for get class name.

    :return: Class name
    :rtype: str

    """
    if isinstance(obj, type):
        return obj.__name__
    return obj.__class__.__name__


class BindingDict(MutableMapping):
    """
    This dict-like object is used to store fields on a serializer.

    This ensures that whenever fields are added to the serializer we call
    `field.bind()` so that the `field_name` and `parent` attributes
    can be set correctly.

    """

    def __init__(self, serializer):
        """

        :param rest_framework.serializers.serializers.BaseSerializer serializer: Serializer for fields.

        """
        self.serializer = serializer
        self.fields = OrderedDict()

    def __setitem__(self, key, field):
        """
        Standard set value and call bind method on field.

        """
        self.fields[key] = field
        field.bind(field_name=key, parent=self.serializer)

    def __getitem__(self, key):
        return self.fields[key]

    def __delitem__(self, key):
        del self.fields[key]

    def __iter__(self):
        return iter(self.fields)

    def __len__(self):
        return len(self.fields)

    def __repr__(self):
        return dict.__repr__(self.fields)
