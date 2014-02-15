# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod, abstractproperty

from .const import RT_SOURCE_TYPE, SQL_SOURCE_TYPE, XML_SOURCE_TYPE


__all__ = ['RT', 'ODBC', 'XML', 'MysqlCertificate',
           'MysqlSource', 'MssqlSource', 'PgsqlSource']


class AbstractIndexType(object):
    __metaclass__ = ABCMeta

    @abstractmethod  # pragma: no cover
    def get_option_dicts(index, attrs_conf):
        """"""

    @abstractproperty  # pragma: no cover
    def source_type():
        """"""


class RT(AbstractIndexType):
    source_type = RT_SOURCE_TYPE

    def get_option_dicts(self, index, attrs_options):
        option_dicts = {}

        for index_name in index.get_index_names():
            options = {}
            options['type'] = self.source_type
            options.update(attrs_options)

            option_dicts[index_name] = options

        return option_dicts


class AbstractSourceType(AbstractIndexType):

    def get_option_dicts(self, index, attrs_options):
        option_dicts = {}

        for index_name in index.get_index_names():
            source_name = index_name
            option_dicts['source %s' % source_name] = attrs_options

            index_options = self.get_index_options(index)
            index_options['source'] = source_name
            option_dicts['index %s' % source_name] = index_options

        return option_dicts

    def get_source_options(self, index, attrs_options):
        print attrs_options
        return source_options

    def get_index_options(self, index):
        return {}

    @abstractmethod  # pragma: no cover
    def get_source_options(self):
        """"""


class ODBC(AbstractSourceType):
    source_type = SQL_SOURCE_TYPE

    def __init__(self, dsn):
        self.dsn = dsn

    def get_source_options(self):
        return {'%s_dsn' % self.source_type: self.dsn}


class XML(AbstractSourceType):
    source_type = XML_SOURCE_TYPE

    def __init__(self, command, fixup_utf8=None):
        self.command = command
        self.fixup_utf8 = fixup_utf8

    def get_option_dicts(self):
        option_dicts = {}

        source_options = {}
        source_options['%s_command' % self.source_type] = self.command
        if self.fixup_utf8 is not None:
            source_options['xmlpipe_fixup_utf8'] = int(bool(self.fixup_utf8))

        return option_dicts


class BaseDB(AbstractSourceType):
    source_type = SQL_SOURCE_TYPE

    def __init__(self, type=None, host=None, port=None,
                 sock=None, db=None, user=None, password=None):
        self.host = host
        self.port = port
        self.sock = sock
        self.db = db
        self.user = user
        self.password = password
        self.type = type

    def get_source_options(self):
        source_options = {'type': self.type}
        source_type = self.source_type

        if self.sock:
            source_options['%s_sock' % source_type] = self.sock
        else:
            source_options['%s_host' % source_type] = self.host
            source_options['%s_port' % source_type] = self.port

        source_options['%s_db' % source_type] = self.db
        source_options['%s_user' % source_type] = self.user
        source_options['%s_password' % source_type] = self.password

        return source_options


class MysqlCertificate(object):
    def __init__(self, cert, key, ca):
        self.cert = cert
        self.key = key
        self.ca = ca

    def get_options(self):
        source_options = {}
        source_options['mysql_ssl_cert'] = self.cert
        source_options['mysql_ssl_key'] = self.key
        source_options['mysql_ssl_ca'] = self.ca
        return source_options


class MysqlSource(BaseDB):
    def __init__(self, *args, **kwargs):
        self.certificate = kwargs.get('certificate')
        super(MysqlSource, self).__init__('mysql', *args, **kwargs)

    def get_source_options(self):
        source_options = super(MysqlSource, self).get_source_options()
        if self.certificate:
            cert_options = self.certificate.get_options()
            source_options.update(cert_options)
        return source_options


class MssqlSource(BaseDB):
    def __init__(self, *args, **kwargs):
        self.winauth = kwargs.get('winauth')
        self.unicode = kwargs.get('unicode')
        super(MssqlSource, self).__init__('mssql', *args, **kwargs)

    def get_source_options(self):
        source_options = super(MssqlSource, self).get_source_options()

        if self.winauth is not None:
            source_options['mssql_winauth'] = int(bool(self.winauth))
        if self.unicode is not None:
            source_options['mssql_unicode'] = int(bool(self.unicode))

        return source_options


class PgsqlSource(BaseDB):
    def __init__(self, *args, **kwargs):
        super(PgsqlSource, self).__init__('pgsql', *args, **kwargs)



