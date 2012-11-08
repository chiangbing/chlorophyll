# -*- coding:utf-8 -*-

import utils
import prims
import string

utils.reseed()

PATH_CHRSET = list(string.lowercase) + ['_', '-']
PATH_SEP = '/'

def rand_path(min_fn=1, max_fn=10, 
              min_depth=1, max_depth=5, 
              prefix=[], suffix=[],
              abs=True):
    prefix = prefix is None and [] or prefix
    suffix = suffix is None and [] or suffix
    seen_len = len(prefix) + len(suffix)

    depth = prims.rand_int(min_depth, max_depth)
    depth = max(seen_len, depth)
    parts = []

    for _ in range(seen_len, depth):
        fn = prims.rand_str(min_len=min_fn, max_len=max_fn, chrset=PATH_CHRSET)
        parts.append(fn)

    parts = prefix + parts + suffix
    p = PATH_SEP.join(parts)
    if abs and p[0:1] != PATH_SEP:
        p = PATH_SEP + p

    return p

def path_gen(min_fn=1, max_fn=10,
             min_depth=1, max_depth=5,
             prefix=[], suffix=[]):
    """Path generator."""
    for x in utils.x_gen(rand_path, min_fn, max_fn, min_depth, max_depth, prefix, suffix):
        yield x


if __name__ == '__main__':
    import time

    for x in path_gen(min_depth=2):
        print x
        time.sleep(0.1)