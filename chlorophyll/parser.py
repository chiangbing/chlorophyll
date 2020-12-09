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
    print("Illegal character '%s'" % t.value[0])

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

parser = yacc.yacc()