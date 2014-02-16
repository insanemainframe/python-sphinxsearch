# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os.path import join

from ..query.filters import Range


def index_to_str(*index):
    if len(index) == 1:
        index = index[0]
        if isinstance(index, basestring):
            return unicode(index)
        else:
            return ' '.join(index.get_index_names())
    elif len(index) == 2:
        return ' '.join(index)
    else:
        raise ValueError('index must be two strings or have get_index_names method ')


class CmdUnknownOptionException(Exception):
    def __init__(self, option):
        msg = ', '.join(keys)
        super(CmdUnknownOptionException, self).__init__(msg)


class CmdOptionConflictException(Exception):
    def __init__(self, option, keys):
        super(CmdOptionConflictException, self).__init__()
        self.option = option
        self.conflicted = ', '.join(keys)


class CmdRequiredOptionException(Exception):
    pass


def check_options(kwargs):
    if kwargs:
        raise CmdUnknownOptionException(kwargs.keys())


def requires_kwarg(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if name not in kwargs:
                raise CmdRequiredOptionException(name)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def cmd_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            cmd_splitted = func(*args, **kwargs)
        except CmdUnknownOptionException as e:
            raise TypeError("%s are an invalid keyword arguments for this function" % e.message)
        except CmdRequiredOptionException as e:
            raise TypeError("you must provide '%s' argument" % e.message)
        except CmdOptionConflictException as e:
            option, conflicted = e.option, e.conflicted
            raise TypeError('option %s conflictz with options; %s' % (option, conflicted))
        else:
            return ' '.join(cmd_splitted)
    return wrapper


def cmd_option(name, option, default):
    def decorator(func):
        def wrapper(*args, **kwargs):
            option_value = kwargs.pop(name, default)
            cmd_splitted = list(func(*args, **kwargs))
            if option_value:
                cmd_splitted.append(option)
            return cmd_splitted
        return wrapper
    return decorator


def cmd_named_option(name, option, default=None, apply=None, conflicts=None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            option_value = kwargs.pop(name, default)
            cmd_splitted = list(func(*args, **kwargs))
            if option_value is not None:
                # check conflicts
                if conflicts:
                    conf_keys = [k for k in conflicts if k in kwargs]
                    if conf_keys:
                        raise CmdOptionConflictException(name, conf_keys)

                if callable(apply):
                    option_value = apply(option_value)
                cmd_splitted.append(option)
                cmd_splitted.append(unicode(option_value))
            return cmd_splitted
        return wrapper
    return decorator


def cmd_loglevel_option(func):
    def wrapper(*args, **kwargs):
        level = int(kwargs.pop('logdebug', 0) or 0)

        if not level:
            logdebug_str = ''
        elif 1 <= level <= 3:
            level_str = (level - 1) * 'v'
            logdebug_str = '--logdebug%s' % level_str
        else:
            raise TypeError('invalid logdebug level %s' % level)

        cmd_splitted = list(func(*args, **kwargs))
        if logdebug_str:
            cmd_splitted.append(logdebug_str)
        return cmd_splitted
    return wrapper


def indexer_cmd(func):
    func = cmd_option('dump', '--dump-rows', False)(func)
    func = cmd_option('sql', '--print-queries', False)(func)
    func = cmd_option('debug', '--verbose', False)(func)
    func = cmd_option('noprogress', '--noprogress', False)(func)
    func = cmd_option('quiet', '--quiet', False)(func)
    func = cmd_decorator(func)
    return func


def server_cmd(func):
    func = cmd_decorator(func)
    return func


class Executor(object):
    """
    >>> executor = Executor()
    """
    def __init__(self, prefix=''):
        self.prefix = prefix

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, prefix):
        """
        >>> executor.prefix = u'/usr/local/'
        """
        self._prefix = prefix
        self.search_cmd = join(prefix, 'search')
        self.searchd_cmd = join(prefix, 'searchd')
        self.indexer_cmd = join(prefix, 'indexer')
        self.spelldump_cmd = join(prefix, 'spelldump')
        self.indextool_cmd = join(prefix, 'indextool')
        self.wordbreaker_cmd = join(prefix, 'wordbreaker')

    @property
    def search(self):
        return '%s --config %s' % (self.search_cmd, self.config_path)

    @property
    def searchd(self):
        return '%s --config %s' % (self.searchd_cmd, self.config_path)

    @property
    def indexer(self):
        return '%s --config %s' % (self.indexer_cmd, self.config_path)

    @property
    def spelldump(self):
        return '%s --config %s' % (self.spelldump_cmd, self.config_path)

    @property
    def indextool(self):
        return '%s --config %s' % (self.indextool_cmd, self.config_path)

    @property
    def wordbreaker(self):
        return '%s --config %s' % (self.wordbreaker_cmd, self.config_path)

    def set_conf(self, config_path):
        self.config_path = config_path

    def get_conf(self):
        return self.config_path

    @indexer_cmd
    @cmd_option('rotate', '--rotate', True)
    @cmd_option('sighup_each', '--sighup-each', False)
    @cmd_option('nohup', '--nohup', False)
    def reindex(self, *indexes, **kwargs):
        """
        >>> executor.reindex(Index, rotate=False)
        >>> executor.reindex('main', 'delta', deleted=0)
        >>> executor.reindex(all=True, sighup_each=True, dump='/tmp/dump.sql')
        """
        cmd_splitted = [self.indexer]

        all = kwargs.pop('all', False)

        check_options(kwargs)

        if all:
            cmd_splitted.append('--all')
        else:
            cmd_splitted.extend(map(index_to_str, indexes))

        return cmd_splitted

    @indexer_cmd
    @cmd_option('rotate', '--rotate', True)
    @cmd_option('keep_attrs', '--keep-attrs', False)
    @cmd_option('killlists', '--merge-killlists', False)
    @cmd_option('nohup', '--nohup', False)
    def merge(self, *index, **kwargs):
        """
        >>> executor.merge(Index, rotate=False)
        >>> executor.merge('main', 'delta', deleted=0)
        >>> executor.merge(Main, Delta, deleted=Range(23, 556), rotate=True)
        """
        if kwargs:
            dst_attr, dst_range = kwargs.popitem()
            if isinstance(dst_range, Range):
                start = int(dst_range.start)
                end = int(dst_range.end)
            else:
                start = int(dst_range)
                end = int(dst_range)
            dst_range_str = '%s %s %s' % (dst_attr, start, end)
        else:
            dst_range_str = ''

        check_options(kwargs)

        cmd_splitted = [self.indexer, '--merge']

        index_str = index_to_str(*index)
        cmd_splitted.append(index_str)

        if dst_range_str:
            cmd_splitted.append('--merge-dst-range')
            cmd_splitted.append(dst_range_str)

        return cmd_splitted

    @indexer_cmd
    @cmd_option('freqs', '--buildfreqs', False)
    @requires_kwarg('outputfile')
    @requires_kwarg('limit')
    def buildstops(self, *indexes, **kwargs):
        """
        >>> executor.buildstops(Index, 'main', limit=500, freqs=True, outputfile='/tmp/stops.txt')
        >>> executor.buildstops('main', 'delta', limit=5000, sql=True)
        >>> executor.buildstops(Main, Delta, limit=9000, outputfile='/tmp/stops.txt')
        """
        outputfile = kwargs.pop('outputfile')
        limit = kwargs.pop('limit')

        check_options(kwargs)

        cmd_splitted = [self.indexer]
        cmd_splitted.extend(map(index_to_str, indexes))
        cmd_splitted.append('--buildstops')

        cmd_splitted.append(unicode(outputfile))
        cmd_splitted.append(unicode(int(limit)))
        return cmd_splitted

    @server_cmd
    @cmd_option('pidfile', '--pidfile', False)
    def status(self):
        return [self.searchd, '--status']

    @server_cmd
    @cmd_option('block', '--stopwait', False)
    @cmd_named_option('pidfile', '--pidfile')
    def stop(self):
        return [self.searchd, '--stop']

    @server_cmd
    @cmd_named_option('pidfile', '--pidfile')
    @cmd_named_option('listen', '--listen', conflicts=('host', 'port'))
    @cmd_named_option('port', '--port', conflicts=('listen',))
    @cmd_named_option('host', '--host', conflicts=('listen',))
    @cmd_named_option('index', '--index', apply=index_to_str)
    @cmd_option('iostats', '--iostats', False)
    @cmd_option('cpustats', '--cpustats', False)
    @cmd_option('console', '--console', False)
    @cmd_option('install', '--install', False)
    @cmd_option('delete', '--delete', False)
    @cmd_option('servicename', '--servicename', False)
    @cmd_option('ntservice', '--ntservice', False)
    @cmd_option('safetrace', '--safetrace', False)
    @cmd_option('replay_flags', '--replay-flags', False)
    @cmd_loglevel_option
    def start(self, **kwargs):
        return [self.searchd, '--start']

    @server_cmd
    def restart(self, *args, **kwargs):
        pidfile = kwargs.pop('pidfile', None)
        new_pidfile = kwargs.pop('new_pidfile', pidfile)

        stop_kwargs = dict(block=True)
        start_kwargs = kwargs

        if pidfile:
            stop_kwargs['pidfile'] = pidfile
        if new_pidfile:
            start_kwargs['pidfile'] = new_pidfile

        stop_cmd = self.stop(**stop_kwargs)
        start_cmd = self.start(*args, **start_kwargs)
        return [stop_cmd, ';', start_cmd]
