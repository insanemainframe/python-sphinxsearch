# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tempfile import gettempdir
from os.path import join

from sphinxsearch import SearchServer
from sphinxsearch.models import Index, Int, String, Bool, TimeStamp, MVA, Float, DB

HOST = 'localhost'
PORT = '4321'
TMP_ROOT = join(gettempdir(), 'sphinxsearch_tmp')
MAX_MATCHES = 10000
LOG_DIR = join(TMP_ROOT, 'logs')


class MySearchServer(SearchServer):
    listen = '%s:%s' % (HOST, PORT)
    read_timeout = 5
    client_timeout = 300
    max_children = 0
    pid_file = join(TMP_ROOT, 'searchd.pid')
    max_matches = MAX_MATCHES
    log = join(LOG_DIR, 'searchd.log')
    workers = 'prefork'
    max_filter_values = 8192

    preopen_indexes = True
    seamless_rotate = True


class AbstractProductsIndex(Index):
    __abstract__ = True
    source_type = DB(type='pgsql', host=HOST,
                     port=5432, db='nazya_db',
                     user='nazya', password='pass')

    path = '/var/www/nazya/nazya/var/sphinx/index_data/data_anyshop_products'
    docinfo = 'extern'
    mlock = 0
    morphology = 'stem_enru'
    min_word_len = 2

    charset_type = 'utf-8'
    charset_table = '0..9, A..Z->a..z, _, a..z, U+410..U+42F->U+430..U+44F, U+430..U+44F'
    min_infix_len = 2
    enable_star = 1
    query_info = 'SELECT * FROM "base_nazyaproduct" WHERE id=$id'


class AnyshopProducts(AbstractProductsIndex):
    __abstract__ = True

    nazyacategory_id = Int()
    type = Int()
    seller_id = Int()

    tree_id = Int()
    lft = Int()
    rght = Int()

    name = String()
    orig_name = String()
    item_id = String()
    thumbs = String()
    images = String()
    nazyacategory__item_id = String()

    post_fee = Float()
    current_price = Float()
    orig_price = Float()

    in_stock = Bool()

    modified_at = TimeStamp()
    created_at = TimeStamp()

    property_values_ids = MVA(Int, query='SELECT "base_nazyaproduct_property_values"."nazyaproduct_id"')




my_engine = Engine(server, indexer, api=api)
