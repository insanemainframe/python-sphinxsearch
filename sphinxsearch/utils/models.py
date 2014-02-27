# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from sphinxsearch.logger import validation_logger


def replaced_query(query, **kwargs):
    query = unicode(query)

    for sphinx_placeholder, user_placeholder in kwargs.items():
        old = unicode(user_placeholder)
        new = '$%s' % sphinx_placeholder
        if old in query:
            query = query.replace(old, new)
        else:
            validation_logger.warning("""Can not found user placeholder "%s"
                                         for "%s" sphinx placeholder""" % (old, new))

    return query


