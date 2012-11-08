# -*- coding:utf-8 -*-

import ply.lex as lex
import string

tokens = (
    'PLAIN_STRING',
    'PLACE_HOLDER'
)

t_ignore = string.whitespace

def t_PLAIN_STRING(t):
    r'(?<!\\)"\S*(?<!\\)"'
    t.value = t.lexer.lexmatch.group(0).strip('"')
    return t

def t_PLACE_HOLDER(t):
    r'\$\{(\S+)\}'
    t.value = t.value.strip('${}')
    return t

def t_error(t):
    print "Illegal character '%s'" % t.value[0]

lexer = lex.lex()


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


def _plain_str_gen(s):
    while True:
        yield s

class template(object):

    def __init__(self, filename):
        self._tokens = []
        
        f = open(filename, 'r')
        lexer.input(f.read())
        while True:
            tok = lexer.token()
            if not tok: break
            self._tokens.append(tok)
        f.close()

        self._generators = {}
        for tok in self._tokens:
            if tok.type == 'PLACE_HOLDER':
                self._generators[tok.value] = ""
            elif tok.type == 'PLAIN_STRING':
                self._generators[tok.value] = _plain_str_gen(tok.value)


    def bind(self, var, generator):
        if var not in self._generators:
            raise InvalidBindError('Try to bind non-existing variable ' + var)

        self._generators[var] = generator


    def render(self, num, bindings={}):
        for var, generator in bindings.iteritems():
            self._generators[var] = generator

        # check unbind
        for var, generator in bindings.iteritems():
            if generator == "":
                raise UnBindError('Unbind variable ' + var)

        def _gen():
            for _ in xrange(0, num):
                yield [next(self._generators[t.value]) for t in self._tokens]
        return _gen()
