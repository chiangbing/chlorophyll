# -*- coding:utf-8 -*-

import sys
import random

from . import utils

##############################
# Primitive types Generators #
##############################

# Generate integers
def rand_int(min, max):
    return random.randint(min, max)


def int_gen(min, max):
    """Integer generator."""
    for x in utils.rand_gen(rand_int, min, max):
        yield x

# Generate strings
import string


def rand_str(minlen=1, maxlen=64, chrset=string.ascii_letters + string.digits):
    len_ = minlen
    if minlen != maxlen:
        # a variable-length string
        len_ = rand_int(minlen, maxlen)
    return ''.join(random.choice(chrset) for _ in range(len_))


def str_gen(len_=64, chrset=string.ascii_letters + string.digits):
    """Fixed-length string generator."""
    for x in utils.rand_gen(rand_str, len_, len_, chrset):
        yield x


def varstr_gen(minlen=1, maxlen=64, chrset=string.ascii_letters + string.digits):
    """Variable-length string generator."""
    for x in utils.rand_gen(rand_str, minlen, maxlen, chrset):
        yield x
