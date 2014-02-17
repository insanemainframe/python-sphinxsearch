# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from abc import ABCMeta, abstractproperty

from .expr import BaseExpr


class AbtractSortMode(object):
    __metaclass__ = ABCMeta

    @abstractproperty  # pragma: no cover
    def api_const():
        """"""

    def get_api_option(self, engine):
        return getattr(engine.api, self.api_const)

    @abstractproperty  # pragma: no cover
    def expr():
        """"""

    def __init__(self, expr):
        self.expr = expr

    def get_api_const(self, engine):
        return getattr(engine.api, self.api_const)

    def apply(self, engine):
        engine.api.SetSortMode(self.get_api_const(engine), self.attr_name)

    @classmethod
    def reset(cls, engine):
        sort_relevance = engine.api.SPH_SORT_RELEVANCE
        engine.api.SetSortMode(sort_relevance)

    def __hash__(self):
        return hash(self.api_const, self.attr_name)

    def __repr__(self):
        return 'SetSortMode(%s, %s)' % (self.api_const, self.attr_name)


class Relevance(AbtractSortMode):
    api_const = 'SPH_SORT_RELEVANCE'
    expr = ''


class BaseAttrSortMode(AbtractSortMode):
    def toExtendedMode(self):
        return '%s %s' % (self.expr, self.extended_postfix)


class Asc(BaseAttrSortMode):
    api_const = 'SPH_SORT_ATTR_ASC'
    extended_postfix = 'ASC'


class Desc(BaseAttrSortMode):
    api_const = 'SPH_SORT_ATTR_DESC'
    extended_postfix = 'DESC'


class TimeSegment(BaseAttrSortMode):
    api_const = 'SPH_SORT_TIME_SEGMENTS'

    def toExtendedMode(self):
        raise NotImplementedError()


class Attr(AbtractSortMode):
    def __new__(cls, expr):
        if expr.startswith('-'):
            return Desc(expr[1:])
        elif expr.startswith('~'):
            return TimeSegment(expr[1:])
        else:
            return Asc(expr)


class MultiSort(AbtractSortMode):
    api_const = 'SPH_SORT_EXTENDED'

    def __init__(self, *modes):
        assert len(modes) <= 5, 'you can set max 5 attributes'

        mode_str_list = []

        for mode in modes:
            if isinstance(mode, BaseAttrSortMode):
                mode = mode.toExtendedMode()
            else:
                mode = unicode(mode)
            mode_str_list.append(mode)

        self.expr = ', '.join(mode_str_list)


class Expr(AbtractSortMode):
    api_const = 'SPH_SORT_EXPR'

    def __init__(self, expr):
        if isinstance(expr, BaseExpr):
            expr = expr.toString()
        self.expr = expr

