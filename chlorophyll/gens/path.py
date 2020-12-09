# -*- coding:utf-8 -*-

import string

from .primitive import rand_str
from . import utils

#################################
# Filesystem-related Generators #
#################################

PATH_CHRSET = list(string.ascii_lowercase) * 10 + ['_', '-', '.']
PATH_SEP = '/'


def rand_path(min_fn=1, max_fn=10,
              min_depth=1, max_depth=5,
              prefix=[], suffix=[],
              abs=True):
    _rand_path = lambda: rand_str(minlen=min_fn, maxlen=max_fn, chrset=PATH_CHRSET)
    parts = utils.rand_list(_rand_path,
                            minlen=min_depth,
                            maxlen=max_depth,
                            prefix=prefix,
                            suffix=suffix)

    p = PATH_SEP.join(parts)
    if abs and p[0:1] != PATH_SEP:
        p = PATH_SEP + p

    return p


def path_gen(min_fn=1, max_fn=10,
             min_depth=1, max_depth=5,
             prefix=[], suffix=[]):
    """Path generator."""
    for x in utils.rand_gen(rand_path,
                         min_fn=min_fn, max_fn=max_fn,
                         min_depth=min_depth, max_depth=max_depth,
                         prefix=prefix, suffix=suffix):
        yield x
