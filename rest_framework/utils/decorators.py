"""
Classes for signature works.

"""
import inspect

########################
# Class decorators     #
########################


def copy_methods_signature(copy_signatures_map):
    """
    Copy signature class decorator.

    :param dict copy_signatures_map: Dict methods names, str types. {from: to, from: to}

    :return: Checking class.
    :rtype: Callable

    """
    def class_decorator(cls):
        for _from, _to in copy_signatures_map.items():
            getattr(cls, _to).__signature__ = inspect.signature(getattr(cls, _from))
        return cls
    return class_decorator


def check_attributes_on_none(*attributes):
    """
    Check class attributes on None.

    :param Iterable attributes: Attributes names for check.

    :return: Checking class.
    :rtype: Callable

    """
    def class_decorator(cls):
        for attr_name in attributes:
            if getattr(cls, attr_name, None) is None:
                raise AttributeError(
                    'The attribute `{}` in class `{}` not configure. '
                    'Please check your class.'.format(attr_name, cls)
                )
        return cls
    return class_decorator
