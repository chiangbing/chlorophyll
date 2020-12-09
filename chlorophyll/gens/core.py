# -*- coding:utf-8 -*-

from typing import types

from . import utils
from .http import *
from .path import *
from .primitive import *
from .tels import *


class GeneratorNotFound(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def resolve(name, builtins=True, funcs=None):
    """Get register generator from name."""
    if builtins:
        # search the builtin *_gen functions
        gen_name = name + '_gen'
        if gen_name in globals():
            return globals()[gen_name]

    # search in custom functions
    if funcs is not None:
        for f in funcs:
            if f.__name__ == name:
                # not sure it's a generator or function
                if type(f) is types.GeneratorType:
                    return f
                else:
                    return utils.create_func_gen(f)

    # search in global functions
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

