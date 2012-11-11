# -*- coding:utf-8 -*-

##################
# Template Lexer #
##################

import gens

import ply.lex as lex
import ply.yacc as yacc
import string
import itertools

from ply.lex import TOKEN

tokens = (
    'LPAREN',
    'RPAREN',
    'LVARBOUND',
    'RVARBOUND',
    'COMMA',
    'EQUAL',
    'AMPERSAND',
    'IDENTIFIER',
    'LITERAL',
    'INTEGER',
    'FLOAT'
)

# ignore all whitespace
t_ignore = string.whitespace

quote = r'(?<!\\)"'
lparen = r'\('
rparen = r'\)'
lvarbound = r'\$\{'
rvarbound = r'\}'
equal = r'\='
comma = r'\,'
ampersand = r'\&'
identifier = r'[_A-Za-z][_\w]*'

t_LPAREN = lparen
t_RPAREN = rparen
t_LVARBOUND = lvarbound
t_RVARBOUND = rvarbound
t_COMMA = comma
t_EQUAL = equal
t_AMPERSAND = ampersand
t_IDENTIFIER = identifier

t_ignore_COMMENT = r'\#.*'

literal = quote + r'(?P<name>([^"]|(?<=\\)")*)' + quote
@TOKEN(literal)
def t_LITERAL(t):
    t.value = t.lexer.lexmatch.group('name').replace(r'\"', r'"')
    return t

integer = r'\d+'
@TOKEN(integer)
def t_INTEGER(t):
    t.value = int(t.value)
    return t


fraction = r'\d*\.\d+'
@TOKEN(fraction)
def t_FLOAT(t):
    t.value = float(t.value)
    return t


def t_error(t):
    print "Illegal character '%s'" % t.value[0]

lexer = lex.lex()


###################
# Template Parser #
###################

def p_template(p):
    '''template : expression template
                | empty'''
    if len(p) == 3:
        p[0] = [p[1]] + p[2]
    elif len(p) == 2:
        p[0] = []


def p_empty(p):
    '''empty : '''
    pass


def p_expression(p):
    '''expression : literal
                  | variable
                  | reference
                  | evaluation'''
    p[0] = p[1]


def p_literal(p):
    '''literal : LITERAL'''
    p[0] = ('LITERAL', p[1])


def p_variable(p):
    '''variable : LVARBOUND IDENTIFIER RVARBOUND'''
    p[0] = ('VARIABLE', p[2])


def p_reference(p):
    '''reference : AMPERSAND IDENTIFIER'''
    p[0] = ('REFERENCE', p[2])


def p_evaluation(p):
    '''evaluation : LVARBOUND IDENTIFIER EQUAL function RVARBOUND
                  | LVARBOUND EQUAL function RVARBOUND'''
    if len(p) == 6:
        p[0] = ('EVALUATION', p[2], p[4])
    elif len(p) == 5:
        p[0] = ('EVALUATION', '_', p[3])  # anounymous evaluation


def p_function(p):
    '''function : IDENTIFIER
                | IDENTIFIER LPAREN RPAREN
                | IDENTIFIER LPAREN arg_list RPAREN'''
    if len(p) == 2:
        p[0] = ('FUNCTION', p[1])
    elif len(p) == 4:
        p[0] = ('FUNCTION', p[1])
    elif len(p) == 5:
        p[0] = ('FUNCTION', p[1], p[3])


def p_arg_list(p):
    '''arg_list : arg_item
                | arg_item COMMA arg_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]


def p_arg_item(p):
    '''arg_item : arg
                | kwarg'''
    p[0] = p[1]


def p_arg(p):
    '''arg : value'''
    p[0] = ('ARG', p[1])


def p_kwarg(p):
    '''kwarg : IDENTIFIER EQUAL value'''
    p[0] = ('KWARG', p[1], p[3])


def p_value(p):
    '''value : literal
             | number
             | function
             | reference'''
    p[0] = p[1]


def p_number(p):
    '''number : INTEGER
              | FLOAT'''
    p[0] = ('NUMBER', p[1])


def p_error(p):
    pass

parser = yacc.yacc(debug=1)


#######################
# Core Template Class #
#######################

class InvalidBindError(Exception):
    '''This error occurs when user try to bind a not existing variable.'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class UnBindError(Exception):
    '''This error occurs when user try to render a template not complete all
    variable binding yet.
    '''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class DuplicateNameError(Exception):
    '''Duplicate name found.'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FunctionNotFound(Exception):
    '''Function not found.'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NotSupportedYetError(Exception):
    '''Not support yet.'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class InternalParseError(Exception):
    '''Internal parsing error, should not happen.'''
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Template(object):

    def __init__(self, tplstr):
        self.ast = parser.parse(tplstr)
        # keep a map from id to expr handler, include all levels of expression
        self.handlers = {}
        # keep a ordered list of id, only top level expressions
        self.exprids = []
        # refs = {var => [ref_id1, ref_id2, ...]}
        self.refs = {}
        # auto-increase id
        self.id = 0

        # travel through all expressions
        for expr in self.ast:
            self._handle_expr(expr)

        self._resolve_refs()

    def bind(self, var, handler):
        '''Bind a variable.'''
        if var not in self.handlers:
            raise InvalidBindError('Try to bind non-existing variable ' + var)
        self.handlers[var] = handler
        self._resolve_refs_for_var(var)

    def render(self, num, bindings={}):
        '''Render this template.'''
        for var, handler in bindings.iteritems():
            self.handlers[var] = handler

        # check unbind
        for var, handler in self.handlers.iteritems():
            if handler is None:
                raise UnBindError('Unbind variable ' + var)

        def _gen():
            for _ in xrange(0, num):
                yield (next(self.handlers[i]) for i in self.exprids)
        return _gen()

    def _handle_expr(self, expr):
        eid, hndler = None, None
        if expr[0] == 'LITERAL':
            eid, hndler = self._handle_literal(expr)
        elif expr[0] == 'VARIABLE':
            eid, hndler = self._handle_variable(expr)
        elif expr[0] == 'REFERENCE':
            eid, hndler = self._handle_ref(expr)
        elif expr[0] == 'EVALUATION':
            eid, hndler = self._handle_evaluation(expr)
        else:
            raise InternalParseError('Unkown expression type.')
        self._add_expr_handler(eid, hndler)

    def _handle_literal(self, expr):
        '''Handle literal.'''
        assert expr[0] == 'LITERAL'
        eid = self._nextid()
        hndler = itertools.repeat(expr[1])
        return eid, hndler

    def _handle_variable(self, expr):
        '''Handle variable.'''
        assert expr[0] == 'VARIABLE'
        eid = expr[1]
        hndler = None   # unbind now
        return eid, hndler

    def _handle_ref(self, expr):
        '''Handle reference.'''
        assert expr[0] == 'REFERENCE'
        # set a empty Reference now and resolve later
        eid = self._nextid()
        hndler = Reference(handler=None)
        # add eid to self.refs
        if not expr[1] in self.refs:
            self.refs[expr[1]] = []
        self.refs[expr[1]].append(eid)
        return eid, hndler

    def _handle_evaluation(self, expr):
        '''Handle evaluation.'''
        assert expr[0] == 'EVALUATION'
        eid = expr[1]
        if eid == '_':
            eid = self._nextid()
        hndler = self._func_handler(expr[2])
        return eid, hndler

    def _add_expr_handler(self, eid, handler):
        if eid in self.handlers:
            raise DuplicateNameError('Duplicate name found: ' + eid)
        self.handlers[eid] = handler
        self.exprids.append(eid)
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
        # resolve function
        try:
            gen = gens.gens(expr[1])
            if gen is None:
                raise FunctionNotFound('Function not found: ' + expr[1])
            return gen(*vargs, **kwargs)
        except TypeError:
            # retry with search_gens=False
            gen = gens.gens(expr[1], search_gens=False)
            if gen is None:
                raise FunctionNotFound('Function not found: ' + expr[1])
            return gen(*vargs, **kwargs)

    def _func_arg_val(self, val):
        if val[0] == 'LITERAL' or val[0] == 'NUMBER':
            return val[1]
        elif val[0] == 'REFERENCE':
            eid, hndler = self._handle_ref(val)
            # add to self.handlers but not self.exprs
            self.handlers[eid] = hndler
            return hndler
        elif val[0] == 'FUNCTION':
            return self._func_handler(val)

    def _resolve_refs(self):
        '''Resolve reference table.'''
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
    '''Reference to function or variable.'''
    def __init__(self, handler=None):
        self.handler = handler

    def __iter__(self):
        return self

    def next(self):
        if self.handler is None:
            return None
        else:
            return next(self.handler)


# test
def test_expr(str):
    import pprint
    result = parser.parse(str)
    print str, '=> ',
    pprint.pprint(result)

if __name__ == '__main__':
    test_expr(r'"123"')
    test_expr(r'${var}')
    test_expr(r'#ref')
    test_expr(r'${=func}')
    test_expr(r'${=func()}')
    test_expr(r'${=func(a="123", b=456)}')
    test_expr(r'${myfunc=func(strarg="123", refarg=#var)}')
    test_expr(r'${myfunc=func(a=substr(s="123", start=1, len=2), b=123, c="456")}')

    test_expr(r'"123" ${myfunc=func(strarg="123", refarg=#var)}')


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
