# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from ..utils import IndexerBlock, ServerBlock


class Engine(object):

    def __init__(self, server, indexer, api):
        self.api = api
        self.server = server
        self.indexer = indexer
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
            if index.__abstract__:
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


class BlockConfMixin(object):
    def get_conf_blocks(self, engine):
        options_dict = {}
        for name in self.options:
            if not hasattr(self, name):
                continue
            options_dict[name] = getattr(self, name)

        return [self.block_type('', **options_dict)]


class Indexer(BlockConfMixin):
    block_type = IndexerBlock
    options = ['mem_limit', 'max_iops',
               'max_iosize', 'max_xmlpipe2_field',
               'write_buffer', 'max_file_field_buffer',
               'on_file_field_error']


class SearchServer(BlockConfMixin):
    block_type = ServerBlock
    options = ['listen', 'address',
               'port', 'log',
               'query_log', 'query_log_format',
               'read_timeout', 'client_timeout',
               'max_children', 'pid_file',
               'max_matches', 'seamless_rotate',
               'preopen_indexes', 'unlink_old',
               'attr_flush_period', 'ondisk_dict_default',
               'max_packet_size', 'mva_updates_pool',
               'crash_log_path', 'max_filters',
               'max_filter_values', 'listen_backlog',
               'read_buffer', 'read_unhinted',
               'max_batch_queries', 'subtree_docs_cache',
               'subtree_hits_cache', 'workers',
               'dist_threads', 'binlog_path',
               'binlog_flush', 'binlog_max_log_size',
               'collation_server', 'collation_libc_locale',
               'plugin_dir', 'mysql_version_string',
               'rt_flush_period', 'thread_stack',
               'expansion_limit', 'compat_sphinxql_magics',
               'watchdog', 'prefork_rotation_throttle']

