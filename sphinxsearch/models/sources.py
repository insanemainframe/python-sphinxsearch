# -*- coding: utf-8 -*-
from abc import ABCMeta

from .attrs import AbstractAttr
from .types import AbstractIndexType
from ..utils import is_abstract, set_abstract


class IndexMeta(ABCMeta):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        src_cls = ABCMeta.__new__(cls, cls_name, cls_parents, cls_dict)

        is_base = cls_dict.get('__metaclass__') == cls
        is_abc = is_base or cls_dict.pop('__abstract__', False)

        set_abstract(src_cls, is_abc)

        cls_attr_names = [nm for nm in dir(src_cls) if not nm.startswith('__')]

        cls_dict = dict([(name, getattr(src_cls, name)) for name in cls_attr_names])

        if not is_abstract(src_cls):
            cls.validate(src_cls)
            source_attrs_dict = {}

            for name, attr in cls_dict.items():
                if isinstance(attr, AbstractAttr):
                    source_attrs_dict[name] = attr

            src_cls.__attrs__ = source_attrs_dict

        return src_cls

    @staticmethod
    def validate(src_cls):
        assert hasattr(src_cls, '__source__')
        assert isinstance(src_cls.__source__, AbstractIndexType)


class Index(object):
    __metaclass__ = IndexMeta
    __delta__ = False

    #
    @classmethod
    def get_option_dicts(cls, engine):
        if is_abstract(cls):
            raise NotImplementedError('Cannot get conf for abstract index')

        source_type = cls.__source__.source_type

        attr_conf_options = {}

        for name, attr in cls.__attrs__.items():
            key, value = attr.get_option(name, source_type)
            attr_conf_options[key] = value

        return cls.__source__.get_option_dicts(cls, attr_conf_options)

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
