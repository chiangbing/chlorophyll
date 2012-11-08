# -*- coding:utf-8 -*-

import utils
import sys
import random
import time

utils.reseed()

# Generate integers
def rand_int(min=0, max=sys.maxint):
    return random.randint(min, max)

def int_gen(min=0, max=sys.maxint):
    """Integer generator."""
    for x in utils.x_gen(rand_int, min, max):
        yield x

# Generate strings
import string

def rand_str(min_len=1, max_len=64, chrset=string.letters+string.digits):
    len_ = min_len
    if min_len != max_len:
        # a variable-length string
        len_ = rand_int(min_len, max_len)
    return ''.join(random.choice(chrset) for _ in xrange(len_))

def str_gen(len_=64, chrset=string.letters+string.digits):
    """Fixed-length string generator."""
    for x in utils.x_gen(rand_str, len_, len_, chrset):
        yield x

def varstr_gen(min_len=1, max_len=64, chrset=string.letters+string.digits):
    """Variable-length string generator."""
    for x in utils.x_gen(rand_str, min_len, max_len, chrset):
        yield x
        

# test
if __name__ == '__main__':
    for s in varstr_gen(10, 100):
        print s
        time.sleep(0.1)
