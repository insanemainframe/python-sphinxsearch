# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractmethod, abstractproperty

from .const import (SQL_SOURCE_TYPE, XML_SOURCE_TYPE, RT_SOURCE_TYPE,
                    RANGE_QUERY_START, RANGE_QUERY_END)


class AbstractAttr(object):
    __metaclass__ = ABCMeta

    @abstractmethod  # pragma: no cover
    def get_option(self, attr_name, source_type):
        """"""


class AbstractUnitAttr(AbstractAttr):
    @abstractproperty  # pragma: no cover
    def type_str():
        """"""

    def get_option(self, attr_name, source_type):
        return '%s_attr_%s' % (source_type, self.type_str), attr_name


class Int(AbstractUnitAttr):
    type_str = 'uint'


class BigInt(AbstractUnitAttr):
    type_str = 'bigint'


class Bool(AbstractUnitAttr):
    type_str = 'bool'


class Float(AbstractUnitAttr):
    type_str = 'float'


class TimeStamp(AbstractUnitAttr):
    type_str = 'timestamp'


class String(AbstractUnitAttr):
    type_str = 'string'


class StringOrd(AbstractUnitAttr):
    type_str = 'str2ordinal'


class WordCount(AbstractUnitAttr):
    type_str = 'str2wordcount'


class MVA(AbstractAttr):
    def __init__(self, attr_type, query=None):
        assert issubclass(attr_type, AbstractUnitAttr), u'attr_type mut be AbstractUnitAttr subtype'
        self.attr_type_str = attr_type.type_str
        self.attr_type = attr_type
        self._query = query

    @property
    def query(self):
        if self._query:
            return '\\n'.join(self._query.split('\n'))
        return None

    def get_rt_option(self, attr_name):
        if self.attr_type in (Int, TimeStamp):
            type_postfix = ''
        elif issubclass(self.attr_type, BigInt):
            type_postfix = '64'
        else:
            raise TypeError('')

        key = '%s_attr_multi%s' % (RT_SOURCE_TYPE, type_postfix)
        return key, attr_name

    def get_xml_option(self, attr_name):
        if self.attr_type in (Int, TimeStamp):
            type_postfix = ''
        elif issubclass(self.attr_type, BigInt):
            type_postfix = '64'
        else:
            raise RuntimeError('Unknown attr_type: %s' % type(self.attr_type))
        key = '%s_attr__attr_multimulti%s' % (XML_SOURCE_TYPE, type_postfix)
        return key, attr_name

    def get_sql_option(self, attr_name):
        if not self.query:
            target = 'field'
        elif RANGE_QUERY_END in self.query and RANGE_QUERY_START in self.query:
            target = 'ranged-query;\n%s' % self.query
        else:
            target = 'query;\n%s' % self.query

        key = 'sql_attr_multi'
        value = '%s %s from %s' % (self.attr_type_str, attr_name, target)
        return key, value

    def get_option(self, attr_name, source_type):
        if source_type == SQL_SOURCE_TYPE:
            return self.get_sql_option(attr_name)
        elif source_type == XML_SOURCE_TYPE:
            return self.get_xml_option(attr_name)
        elif source_type == RT_SOURCE_TYPE:
            return self.get_rt_option(attr_name)
        else:
            raise RuntimeError('Unknown source_type: %s' % source_type)


__all__ = ['Int', 'BigInt', 'Bool', 'Float', 'TimeStamp',
           'String', 'StringOrd', 'WordCount', 'MVA']
