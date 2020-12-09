# -*- coding:utf-8 -*-

import itertools
from . import gens
from .parser import parser

#######################
# Core Template Class #
#######################


class InvalidBindError(Exception):
    """This error occurs when user try to bind a not existing variable."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnBindError(Exception):
    """This error occurs when user try to render a template not complete all
    variable binding yet.
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DuplicateNameError(Exception):
    """Duplicate name found."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FunctionNotFound(Exception):
    """Function not found."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotSupportedYetError(Exception):
    """Not support yet."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InternalParseError(Exception):
    """Internal parsing error, should not happen."""
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Chlorophyll(object):

    def __init__(self, tpl, funcs=[]):
        self.funcs = funcs
        self.ast = parser.parse(tpl)
        # keep a map from id to expr handler, include all levels of expression
        self.handlers = {}
        # keep a ordered list of id, only top level expressions
        self.expr_ids = []
        # refs = {var => [ref_id1, ref_id2, ...]}
        self.refs = {}
        # auto-increase id
        self.id = 0

        # travel through all expressions
        for expr in self.ast:
            self._handle_expr(expr)

        self._resolve_refs()

    def bind(self, var, handler):
        """Bind a variable."""
        if var not in self.handlers:
            raise InvalidBindError('Try to bind non-existing variable ' + var)
        self.handlers[var] = handler
        self._resolve_refs_for_var(var)

    def render(self, num, bindings=None):
        """Render this template."""
        if bindings is not None:
            for var, handler in iter(bindings.items()):
                self.handlers[var] = handler

        # check unbind
        for var, handler in iter(self.handlers.items()):
            if handler is None:
                raise UnBindError('Unbind variable ' + var)

        for _ in range(0, num):
            yield ([next(self.handlers[i]) for i in self.expr_ids])

    def _handle_expr(self, expr):
        if expr[0] == 'LITERAL':
            eid, handler = self._handle_literal(expr)
        elif expr[0] == 'VARIABLE':
            eid, handler = self._handle_variable(expr)
        elif expr[0] == 'REFERENCE':
            eid, handler = self._handle_ref(expr)
        elif expr[0] == 'EVALUATION':
            eid, handler = self._handle_evaluation(expr)
        else:
            raise InternalParseError('Unknown expression type.')
        self._add_expr_handler(eid, handler)

    def _handle_literal(self, expr):
        """Handle literal."""
        assert expr[0] == 'LITERAL'
        eid = self._nextid()
        hndler = itertools.repeat(expr[1])
        return eid, hndler

    def _handle_variable(self, expr):
        """Handle variable."""
        assert expr[0] == 'VARIABLE'
        eid = expr[1]
        handler = None   # unbind now
        return eid, handler

    def _handle_ref(self, expr):
        '''Handle reference.'''
        assert expr[0] == 'REFERENCE'
        # set a empty Reference now and resolve later
        eid = self._nextid()
        handler = Reference(handler=None)
        # add eid to self.refs
        if not expr[1] in self.refs:
            self.refs[expr[1]] = []
        self.refs[expr[1]].append(eid)
        return eid, handler

    def _handle_evaluation(self, expr):
        """Handle evaluation."""
        assert expr[0] == 'EVALUATION'
        eid = expr[1]
        if eid == '_':
            eid = self._nextid()
        handler = self._func_handler(expr[2])
        return eid, handler

    def _add_expr_handler(self, eid, handler):
        if eid in self.handlers:
            raise DuplicateNameError('Duplicate name found: ' + eid)
        self.handlers[eid] = handler
        self.expr_ids.append(eid)
        return eid

    def _nextid(self):
        self.id += 1
        return '_ID_' + str(self.id)

    def _func_handler(self, expr):
        assert expr[0] == 'FUNCTION'
        # resolve arguments
        vargs = []
        kwargs = {}
        if len(expr) > 2:
            # have args
            for arg_item in expr[2]:
                if arg_item[0] == 'ARG':
                    vargs.append(self._func_arg_val(arg_item[1]))
                elif arg_item[0] == 'KWARG':
                    kwargs[arg_item[1]] = self._func_arg_val(arg_item[2])
                else:
                    raise InternalParseError('Unknow function arg_item type: ' + arg_item[0])
        # resolve generator
        gen = gens.resolve(expr[1], funcs=self.funcs)
        return gen(*vargs, **kwargs)

    def _func_arg_val(self, val):
        if val[0] == 'LITERAL' or val[0] == 'NUMBER':
            return val[1]
        elif val[0] == 'REFERENCE':
            eid, handler = self._handle_ref(val)
            # add to self.handlers but not self.exprs
            self.handlers[eid] = handler
            return handler
        elif val[0] == 'FUNCTION':
            return self._func_handler(val)

    def _resolve_refs(self):
        """Resolve reference table."""
        for var in self.refs.keys():
            if self.handlers[var] is None:
                # unbind yet
                continue
            else:
                self._resolve_refs_for_var(var)

    def _resolve_refs_for_var(self, var):
        ref_list = self.refs[var]
        gs = itertools.tee(self.handlers[var], len(ref_list) + 1)
        self.handlers[var] = gs[0]
        for i, ref in enumerate(ref_list):
            self.handlers[ref].handler = gs[i + 1]


class Reference(object):
    """Reference to function or variable."""
    def __init__(self, handler=None):
        self.handler = handler

    def __iter__(self):
        return self

    def __next__(self):
        if self.handler is None:
            return None
        else:
            return next(self.handler)


# test
# def test_expr(str):
#     import pprint
#     result = parser.parse(str)
#     print(str, '=> ', end='')
#     pprint.pprint(result)
#
# if __name__ == '__main__':
#     test_expr(r'"123"')
#     test_expr(r'${var}')
#     test_expr(r'#ref')
#     test_expr(r'${=func}')
#     test_expr(r'${=func()}')
#     test_expr(r'${=func(a="123", b=456)}')
#     test_expr(r'${myfunc=func(strarg="123", refarg=#var)}')
#     test_expr(r'${myfunc=func(a=substr(s="123", start=1, len=2), b=123, c="456")}')
#     test_expr(r'"123" ${myfunc=func(strarg="123", refarg=#var)}')


## Output:
# "123" => [('LITERAL', '123')]
# ${var} => [('VARIABLE', 'var')]
# #ref => [('REFERENCE', 'ref')]
# ${=func} => [('EVALUATION', '_', ('FUNCTION', 'func'))]
# ${=func()} => [('EVALUATION', '_', ('FUNCTION', 'func'))]
# ${=func(a="123", b=456)} => [('EVALUATION',
#   '_',
#   ('FUNCTION',
#    'func',
#    [('KWARG', 'a', ('LITERAL', '123')), ('KWARG', 'b', ('NUMBER', 456))]))]
# ${myfunc=func(strarg="123", refarg=#var)} => [('EVALUATION',
#   'myfunc',
#   ('FUNCTION',
#    'func',
#    [('KWARG', 'strarg', ('LITERAL', '123')),
#     ('KWARG', 'refarg', ('REFERENCE', 'var'))]))]
# ${myfunc=func(a=substr(s="123", start=1, len=2), b=123, c="456")} => [('EVALUATION',
#   'myfunc',
#   ('FUNCTION',
#    'func',
#    [('KWARG',
#      'a',
#      ('FUNCTION',
#       'substr',
#       [('KWARG', 's', ('LITERAL', '123')),
#        ('KWARG', 'start', ('NUMBER', 1)),
#        ('KWARG', 'len', ('NUMBER', 2))])),
#     ('KWARG', 'b', ('NUMBER', 123)),
#     ('KWARG', 'c', ('LITERAL', '456'))]))]
# "123" ${myfunc=func(strarg="123", refarg=#var)} => [('LITERAL', '123'),
#  ('EVALUATION',
#   'myfunc',
#   ('FUNCTION',
#    'func',
#    [('KWARG', 'strarg', ('LITERAL', '123')),
#     ('KWARG', 'refarg', ('REFERENCE', 'var'))]))]
