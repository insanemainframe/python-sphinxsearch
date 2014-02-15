# -*- coding: utf-8 -*-
from __future__ import unicode_literals


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
