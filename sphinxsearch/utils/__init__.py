# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from abc import ABCMeta, abstractproperty

from .const import CONFIG_INDENT


def set_abstract(cls, value):
    cls.__abstract_index__ = value


def is_abstract(cls):
    return cls.__abstract_index__


def options2str(**options):
    return '\n'.join(['%s = %s' % (k, v) for k, v in options.items()])


def add_indent(block_body):
    body_str_list = block_body.split('\n')
    body_str_list = ['%s%s' % (CONFIG_INDENT, s) for s in body_str_list]
    return '\n'.join(body_str_list)


class AbstractConfBlock(dict):
    __metaclass__ = ABCMeta

    @abstractproperty  # pragma: no cover
    def type():
        """"""

    def __init__(self, name, **options):
        self.name = name
        self.options = options

    def __unicode__(self):
        options_body = add_indent(options2str(**self.options))
        return '%s %s\n { \n%s\n }' % (self.type, self.name, options_body)

    def __repr__(self):  # pragma: no cover
        return ('ConfBlock<> %s' % add_indent(self.__unicode__())).encode('utf-8')


class IndexBlock(AbstractConfBlock):
    type = 'index'


class SourceBlock(AbstractConfBlock):
    type = 'source'


class IndexerBlock(AbstractConfBlock):
    type = 'indexer'


class ServerBlock(AbstractConfBlock):
    type = 'searchd'


class ConfAttrProperty(object):
    def __init__(self, name):
        self.name = name
        self.value = None

    def __get__(self, instance, owner):
        return self.value

    def __set__(self, instance, value):
        self.value = value

    def __del__(self, instance):
        self.value = None

    def get_value(self):
        return self.value


class OptionableMeta(type):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        if not hasattr(cls, 'OPTIONS'):
            raise TypeError("Metaclass must provide OPTIONS  attribute")

        for opt_name in cls.OPTIONS:
            opt_prop = ConfAttrProperty(opt_name)
            cls_dict[opt_name] = opt_prop

        src_cls = type.__new__(cls, cls_name, cls_parents, cls_dict)
        return src_cls


class OptionableBase(object):
    def get_options_dict(self):
        opt_dict = {}
        for opt_name in self.__class__.__metaclass__.OPTIONS:
            opt_value = getattr(self, opt_name)
            if opt_value is not None:
                opt_dict[opt_name] = opt_value
        return opt_dict

    def get_options(self):
        return {self.option_block_name: self.get_options_dict()}
