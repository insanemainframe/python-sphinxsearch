# -*- coding: utf-8 -*-
from copy import copy


class FiltersContainer(object):
    def __init__(self, filters_ops):
        self.filters_ops = filters_ops


class BaseFilterOperator(object):
    api_method = NotImplemented

    def __init__(self):
        self.exclude = False

    def apply(self, client, attr_name):
        raise NotImplementedError()

    def revert(self):
        new_instance = copy(self)
        new_instance.exclude = not new_instance.exclude
        return new_instance

    def __repr__(self):
        return "%s(attr_name, %s, %s)" % (self.api_method,
                                          repr(self.values),
                                          self.exclude)


class Any(BaseFilterOperator):
    api_method = 'SetFilter'

    def __init__(self, *values):
        super(Any, self).__init__()
        self.values = map(int, values)

    def apply(self, client, attr_name):
        client.SetFilter(attr_name, self.values, self.exclude)


class All(BaseFilterOperator):
    def __init__(self, *values):
        super(All, self).__init__()
        sub_ops = []

        for value in values:
            if isinstance(value, self.__class__):
                raise ValueError('passing All operator to itself is not allowed')
            if isinstance(value, BaseFilterOperator):
                sub_ops.append(value)
            else:
                sub_ops.append(Any(value))

        self.sub_ops = tuple(sub_ops)

    def revert(self):
        new_instance = copy(self)
        new_instance.sub_ops = [op.revert() for op in new_instance.sub_ops]
        return new_instance

    def __repr__(self):
        return '\n'.join([repr(sub) for sub in self.sub_ops])


class Range(BaseFilterOperator):
    values_type = int
    api_method = 'SetRange'

    def __init__(self, start, end):
        super(Range, self).__init__()
        start, end = map(self.values_type, (start, end))
        assert start < end
        self.start = start
        self.end = end

    def __repr__(self):
        return "%s(attr_name, %s, %s, %s)" % (self.api_method,
                                              self.start,
                                              self.end,
                                              self.exclude)


class FloatRange(Range):
    api_method = 'SetFloatRange'
    values_type = float


class IDRange(Range):
    api_method = 'SetIDRange'

    def revert(self, *args, **kwargs):
        raise RuntimeError('casting Not for IDRange is not allowed')


class Not(object):
    def __new__(cls, value):
        if not isinstance(value, BaseFilterOperator):
            value = Any(value)

        return value.revert()
