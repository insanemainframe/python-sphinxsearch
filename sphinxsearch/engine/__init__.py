# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..utils import is_abstract
from .server import SearchServer
from .indexer import Indexer


class Engine(object):
    def __init__(self):
        self.api = None
        self.server = None
        self.indexer = None
        self.indexes = set()

    def get_conf(self):
        block_str_list = []

        for block in self.get_conf_blocks():
            block_body = unicode(block)
            block_str_list.append(block_body)

        return '\n'.join(block_str_list)

    def save(self, path):
        config_str = self.get_conf()
        with open(path, 'w') as f:
            f.write(config_str)

    def get_conf_blocks(self):
        server_blocks = self.server.get_conf_blocks(self)
        indexer_blocks = self.indexer.get_conf_blocks(self)
        indexes_blocks = self.get_indexes_blocks()
        return indexes_blocks + server_blocks + indexer_blocks

    def get_indexes_blocks(self):
        indexes_blocks = []

        for index in self.indexes:
            if is_abstract(index):
                continue
            indexes_blocks.extend(index.get_conf_blocks(self))

        return filter(bool, indexes_blocks)

    def add_index(self, index):
        self.indexes.add(index)

    def extend_indexes(self, indexes):
        self.indexes.update(indexes)

    def write(self, config_path):
        with open(config_path, 'w') as f:
            s = self.get_conf().encode('utf-8')
            f.write(s)

    def replace(self, **kwargs):
        api = kwargs['api'] if 'api' in kwargs else self.api
        server = kwargs['server'] if 'server' in kwargs else self.server
        indexer = kwargs['indexer'] if 'indexer' in kwargs else self.indexer
        indexes = kwargs['indexes'] if 'indexes' in kwargs else self.indexes

        new_inst = self.__class__(api=api, server=server, indexer=indexer)
        new_inst.extend_indexes(indexes)
        return new_inst

    def session(self, **kwargs):
        if self.server is None:
            raise RuntimeError('Ebgine must provide server')
        if self.api is None:
            raise RuntimeError('Ebgine must provide api')

        return self.server.get_session(self.api, **kwargs)


class BlockConfMixin(object):
    def get_conf_blocks(self, engine):
        options_dict = {}
        for name in self.options:
            if not hasattr(self, name):
                continue
            options_dict[name] = getattr(self, name)

        return [self.block_type('', **options_dict)]


__all__ = ['Engine', 'SearchServer', 'Indexer']
