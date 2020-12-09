# -*- coding:utf-8 -*-

from typing import types

from . import utils
from .http import *
from .path import *
from .primitive import *
from .tels import *

def import_file(file):
    exec(open(file).read(), globals())

class GeneratorNotFound(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def gens(name, search_gens=True):
    '''Get register generator from name.'''
    if search_gens:
        gen_name = name + '_gen'
        if gen_name in globals():
            return globals()[name + '_gen']

    # not search x_gen function
    if name in globals():
        # not sure it's a generator or function
        if type(globals()[name]) is types.GeneratorType:
            return globals()[name]
        else:
            return utils.create_func_gen(globals()[name])
    elif name in globals()['__builtins__']:
        return utils.create_func_gen(globals()['__builtins__'][name])
    else:
        raise GeneratorNotFound('Cannot create generator for ' + name)

