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