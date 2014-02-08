# -*- coding: utf-8 -*-
import re

RE_ESCAPE_STRING = re.compile(r"([=\(\)|\-!@~\"&/\\\^\$\=])")


def escape_string(string):
    return RE_ESCAPE_STRING.sub(r"\\\1", string)
