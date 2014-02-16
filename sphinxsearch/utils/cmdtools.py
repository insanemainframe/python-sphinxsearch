# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function


class CmdUnknownOptionException(Exception):
    def __init__(self, keys):
        msg = ', '.join(keys)
        super(CmdUnknownOptionException, self).__init__(msg)


class CmdOptionConflictException(Exception):
    def __init__(self, option, keys):
        super(CmdOptionConflictException, self).__init__()
        self.option = option
        self.conflicted = ', '.join(keys)


class RequiredOptionException(Exception):
    pass


def requires_kwarg(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if name not in kwargs:
                raise RequiredOptionException(name)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_options(kwargs):
    if kwargs:
        raise CmdUnknownOptionException(kwargs.keys())


def cmd_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            cmd_splitted = func(*args, **kwargs)
        except CmdUnknownOptionException as e:
            raise TypeError("%s are an invalid keyword arguments for this function" % e.message)
        except RequiredOptionException as e:
            raise TypeError("you must provide '%s' argument" % e.message)
        except CmdOptionConflictException as e:
            option, conflicted = e.option, e.conflicted
            raise TypeError('option %s conflictz with options; %s' % (option, conflicted))
        else:
            return ' '.join(cmd_splitted)
    return wrapper


@requires_kwarg('default')
def cmd_flag(name, option, **kwargs):
    default = kwargs.pop('default', None)
    conflicts = kwargs.pop('conflicts', None)
    check_options(kwargs)

    def decorator(func):
        def wrapper(*args, **kwargs):
            option_value = kwargs.pop(name, default)
            cmd_splitted = list(func(*args, **kwargs))
            if option_value:
                cmd_splitted.append(option)
                if conflicts:
                    conf_keys = [k for k in conflicts if k in kwargs]
                    if conf_keys:
                        raise CmdOptionConflictException(name, conf_keys)
            return cmd_splitted
        return wrapper
    return decorator


def cmd_named_kwarg(name, option, **kwargs):
    default = kwargs.pop('default', None)
    conflicts = kwargs.pop('conflicts', None)
    apply = kwargs.pop('apply', None)
    check_options(kwargs)

    def decorator(func):
        def wrapper(*args, **kwargs):
            option_value = kwargs.pop(name, default)
            cmd_splitted = list(func(*args, **kwargs))
            if option_value is not None:
                # check conflicts
                if conflicts:
                    conf_keys = [k for k in conflicts if k in kwargs]
                    if conf_keys:
                        raise CmdOptionConflictException(name, conf_keys)

                if callable(apply):
                    option_value = apply(option_value)
                if option:
                    cmd_splitted.append(option)
                cmd_splitted.append(unicode(option_value))
            return cmd_splitted
        return wrapper
    return decorator


@requires_kwarg('default')
def cmd_named_arg(*args, **kwargs):
    kwargs['option'] = None
    return cmd_named_kwarg(*args, **kwargs)
