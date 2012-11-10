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
    'SHARP',
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
sharp = r'\#'
identifier = r'[_A-Za-z][_\w]*'

t_LPAREN = lparen
t_RPAREN = rparen
t_LVARBOUND = lvarbound
t_RVARBOUND = rvarbound
t_COMMA = comma
t_EQUAL = equal
t_SHARP = sharp
t_IDENTIFIER = identifier

literal = quote + r'(?P<name>([^"]|(?<=\\)")*)' + quote
@TOKEN(literal)
def t_LITERAL(t):
    t.value = t.lexer.lexmatch.group('name')
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
    '''reference : SHARP IDENTIFIER'''
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
    '''arg_list : kwarg
                | kwarg COMMA arg_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]


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

parser = yacc.yacc()


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


class Template(object):

    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.ast = parser(f.read())

        self.exprs = {}
        self.id = 0
        # reference table
        self.refs = {}

        # travel through all expressions
        for expr in self.ast:
            self._handle_expr(expr)

        self._resolve_refs()

    def bind(self, var, generator):
        '''Bind a variable.'''
        if var not in self.exprs:
            raise InvalidBindError('Try to bind non-existing variable ' + var)

        self.exprs[var] = generator
        self._resolve_refs_for_var(var)

    def render(self, num, bindings={}):
        '''Render this template.'''
        for var, generator in bindings.iteritems():
            self.exprs[var] = generator

        # check unbind
        for var, generator in bindings.iteritems():
            if generator == None:
                raise UnBindError('Unbind variable ' + var)

        def _gen():
            for _ in xrange(0, num):
                yield [next(self.exprs[t.value]) for t in self._tokens]
        return _gen()

    def _handle_expr(self, expr):
        if expr[0] == 'LITERAL':
            self._add_expr_handler('_', self._literal_handler(expr[1]))
        elif expr[0] == 'VARIABLE':
            # unbind variable
            self._add_expr_handler(expr[1], None)
        elif expr[0] == 'REFERENCE':
            self._handle_ref(expr)
        elif expr[0] == 'EVALUATION':
            self._add_expr_handler(expr[1], self._func_handler(expr[2]))

    def _handle_ref(self, expr):
            ref_id = self._nextid('_')
            self._ref_handler(ref_id, expr[1])
            # set the real handler for ref when everything is done
            self._add_expr_handler(ref_id, None)

    def _add_expr_handler(self, name, handler):
        if name in self.exprs:
            raise DuplicateNameError('Duplicate name found: ' + name)
        if name == '_':
            name = self._nextid()
        self.exprs[name] = handler

    def _nextid(self):
        self.id += 1
        return '_ID_' + str(self.id)

    def _literal_handler(str):
        return itertools.repeat(str)

    def _ref_handler(self, ref_id, var):
        '''self.refs = {var => [ref_id1, ref_id2, ...]}'''
        if not var in self.refs:
            self.refs[var] = []
        self.refs[var].append(ref_id)

    def _func_handler(self, expr):
        assert expr[0] == 'FUNCTION'

        gen = gens.gens(expr[1])
        if gen is None:
            raise FunctionNotFound('Function not found: ' + expr[1])

        if len(expr) > 2:
            # have args
            kwargs = {}
            for k, v in expr[2]:
                if v[0] == 'LITERAL' or v[0] == 'NUMBER':
                    kwargs[k] = v[1]
                else:
                    raise NotSupportedYetError(
                        'Not support REFERENCE and FUNCTION in arguments yet.')
                # elif v[0] == 'REFERENCE':
                #     self._handle_ref(v)
                # elif v[0] == 'FUNCTION':
        return gen(**kwargs)

    def _resolve_refs(self):
        '''Resolve reference table.'''
        for var in self.refs.keys():
            if self.exprs[var] is None:
                # unbind yet
                continue
            else:
                self._resolve_refs_for_var(var)

    def _resolve_refs_for_var(self, var):
        ref_list = self.refs[var]
        gs = itertools.tee(self.exprs[var], len(ref_list) + 1)
        self.exprs[var] = gs[0]
        for i, ref in enumerate(ref_list):
            self.exprs[ref] = gs[i + 1]


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
