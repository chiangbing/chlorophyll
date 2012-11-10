# -*- coding:utf-8 -*-

import random
import time


def reseed():
    random.seed(int(time.time() * 1000))


def x_gen(func, *args1, **args2):
    if func is None:
        yield None

    count = 0
    while True:
        count += 1
        if count >= 1000000:
            reseed()
            count = 0
        yield func(*args1, **args2)


def prob_choice(prob_map, default=[]):
    """Choose a item based its probability.

    prob_map contains mapping from probability to a list of items, e.g.
        prob_map = {0.99:[1,2,3], 0.01:[5,6,7]}
    and then 1/2/3 will be generated more frequent than 5/6/7.
    """
    rand = random.random()
    base = 0
    for prob, items in prob_map.iteritems():
        if rand >= base and rand < base + prob:
            return random.choice(items)
        base += prob

    # default
    return random.choice(default)


def rand_list(rand_func, minlen, maxlen, prefix=[], suffix=[]):
    if not prefix is None and len(prefix) > 0:
        prefix = [random.choice(prefix)]
    if not suffix is None and len(suffix) > 0:
        suffix = [random.choice(suffix)]

    # if prefix or suffix is not empty, increase seen length by one for each
    seen_len = len(prefix) + len(suffix)
    alen = random.randint(minlen, maxlen)
    alen = max(seen_len, alen)
    parts = [rand_func() for _ in xrange(seen_len, alen)]
    return prefix + parts + suffix
