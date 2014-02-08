# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from itertools import product


def get_api():  # pragma: no cover
    import sphinxapi
    return sphinxapi


def get_servers():
    from sphinxsearch import SearchServer

    class MyServer(SearchServer):
        listen = 'localhost:6543'
        max_children = 10
        pid_file = '/tmp/myserver.pid'

    return [MyServer]


def get_indexers():
    from sphinxsearch import Indexer

    class MyIndexer(Indexer):
        mem_limit = '512M'
    return [MyIndexer]


def get_index_types():
    from sphinxsearch.models import DB, XML, RT

    mysql_type = DB('MySQL', sock='sooo')
    pgsql_type = DB('pgsql', host='localhost', port=5656)
    xml_type = XML('xml_command')
    rt_type = RT()

    return mysql_type, pgsql_type, xml_type, rt_type


def get_schemas():
    from sphinxsearch.models import attrs as a
    from random import shuffle

    numbs = [a.Int(), a.Bool(), a.TimeStamp(), a.BigInt]

    mvas = []
    for atype in [a.Int, a.BigInt]:
        mva1 = a.MVA(atype, query="""SELECT id, tag FROM tags WHERE id>=$start AND id<=$end; \
                                            SELECT MIN(id), MAX(id) FROM tags""")
        mva2 = a.MVA(atype, query="""SELECT id, tag FROM tags WHERE id>=start AND id<=$end; \
                                                   SELECT MIN(id), MAX(id) FROM tags""")
        mva3 = a.MVA(atype)

        mvas.extend([mva1, mva2, mva3])

    schemas = []

    for _ in range(3):
        shuffle(numbs)
        shuffle(mvas)

        schema = {}

        for i, num in enumerate(numbs):
            schema['num_%s' % i] = num

        for i, mva in enumerate(mvas):
            schema['mva_%s' % i] = mva

        schemas.append(schema)

    return schemas


def get_valid_indexes():
    from sphinxsearch import Index

    index_type_list = get_index_types()
    delta_list = [False, True]
    is_abstract_lst = [False, True]
    is_custom_name_lst = [False, True]
    schemas = get_schemas()

    arg_source = product(index_type_list,
                         delta_list,
                         is_abstract_lst,
                         is_custom_name_lst,
                         schemas)

    indexes_classes = []

    for i, args in enumerate(arg_source):
        index_type, is_delta, is_abstract, is_custom_name, schema = args

        cls_name = 'foo_%s' % i
        cls_dict = dict(type=index_type,
                        __abstract__=is_abstract,
                        __delta__=is_delta)

        cls_dict.update(schema)

        if is_custom_name:
            cls_dict['__source_name__'] = 'cust_%s' % cls_name

        cls_parents = (Index,)

        new_cls = type(Index)(str(cls_name), cls_parents, cls_dict)
        indexes_classes.append(new_cls)

    return indexes_classes
