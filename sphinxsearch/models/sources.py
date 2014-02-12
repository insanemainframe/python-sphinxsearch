# -*- coding: utf-8 -*-
from abc import ABCMeta

from .attrs import AbstractAttr
from .types import AbstractIndexType


class IndexMeta(ABCMeta):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        src_cls = ABCMeta.__new__(cls, cls_name, cls_parents, cls_dict)
        src_cls.__abstract__ = '__metaclass__' in cls_dict

        cls_attr_names = [nm for nm in dir(src_cls) if not nm.startswith('__')]

        cls_dict = dict([(name, getattr(src_cls, name)) for name in cls_attr_names])

        if not src_cls.__abstract__:
            cls.validate(cls_name, cls_parents, cls_dict)
            source_attrs_dict = {}

            for name, attr in cls_dict.items():
                if isinstance(attr, AbstractAttr):
                    source_attrs_dict[name] = attr

            src_cls.__attrs__ = source_attrs_dict

        return src_cls

    @staticmethod
    def validate(cls_name, cls_parents, cls_dict):
        assert 'type' in cls_dict
        assert isinstance(cls_dict['type'], AbstractIndexType)


class Index(object):
    __metaclass__ = IndexMeta
    __delta__ = False

    #
    @classmethod
    def get_conf_blocks(cls, engine):
        if cls.__abstract__:
            raise NotImplementedError('Cannot get conf for abstract index')

        source_type = cls.type.source_type

        attr_conf_options = {}

        for name, attr in cls.__attrs__.items():
            key, value = attr.get_option(name, source_type)
            attr_conf_options[key] = value

        return cls.type.get_conf_blocks(cls, attr_conf_options)

    @classmethod
    def get_name(cls):
        if hasattr(cls, '__source_name__'):
            return cls.__source_name__

        name = cls.__name__
        module_name = cls.__module__.split('.')[-1]
        return ('%s_%s' % (module_name, name)).lower()

    @classmethod
    def get_index_names(cls):
        names = (cls.get_name(),)
        if cls.__delta__:
            names = names
        return names
