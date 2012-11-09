# -*- coding:utf-8 -*-

##################
# Template Lexer #
##################

import ply.lex as lex
import ply.yacc as yacc
import string

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

fraction=r'\d*\.\d+'
@TOKEN(fraction)
def t_FLOAT(t):
    t.value = double(t.value)
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

class Template(object):

    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.ast = parser(f.read())

        self.generators = {}
        
        for tok in self._tokens:
            if tok.type == 'VARIABLE':
                self.generators[tok.value] = ""
            elif tok.type == 'LITERAL':
                self.generators[tok.value] = _plain_str_gen(tok.value)


    def bind(self, var, generator):
        if var not in self.generators:
            raise InvalidBindError('Try to bind non-existing variable ' + var)

        self.generators[var] = generator


    def render(self, num, bindings={}):
        for var, generator in bindings.iteritems():
            self.generators[var] = generator

        # check unbind
        for var, generator in bindings.iteritems():
            if generator == "":
                raise UnBindError('Unbind variable ' + var)

        def _gen():
            for _ in xrange(0, num):
                yield [next(self.generators[t.value]) for t in self._tokens]
        return _gen()


# test
def test_expr(str):
    result = parser.parse(str)
    print str, '=>', result

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
