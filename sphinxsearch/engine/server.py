# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..session import Session
from ..utils import OptionableMeta, OptionableBase


class _SearchServerMeta(OptionableMeta):
    OPTIONS = ['log',
               'query_log',
               'query_log_format',
               'read_timeout',
               'client_timeout',
               'max_children',
               'pid_file',
               'max_matches',
               'seamless_rotate',
               'preopen_indexes',
               'unlink_old',
               'attr_flush_period',
               'ondisk_dict_default',
               'max_packet_size',
               'mva_updates_pool',
               'crash_log_path',
               'max_filters',
               'max_filter_values',
               'listen_backlog',
               'read_buffer',
               'read_unhinted',
               'max_batch_queries',
               'subtree_docs_cache',
               'subtree_hits_cache',
               'workers',
               'dist_threads',
               'binlog_path',
               'binlog_flush',
               'binlog_max_log_size',
               'collation_server',
               'collation_libc_locale',
               'plugin_dir',
               'mysql_version_string',
               'rt_flush_period',
               'thread_stack',
               'expansion_limit',
               'compat_sphinxql_magics',
               'watchdog',
               'prefork_rotation_throttle']


class SearchServer(OptionableBase):
    __metaclass__ = _SearchServerMeta
    option_block_name = 'server'

    def __init__(self, host=None, port=None, listen=None):
        if listen and not (host or port):
            self.listen_str = unicode(listen)
        elif host and port:
            self.listen_str = '%s:%s' % (host, port)
            self.host = host
            self.port = port
        else:
            raise ValueError('You nust provide host and port or listen')

    def get_session(self, api, **kwargs):
        return Session(api, self.host, self.port, **kwargs)

    def get_options_dict(self):
        opt_dict = super(SearchServer, self).get_options_dict()
        opt_dict['listen'] = self.listen_str
        return opt_dict
