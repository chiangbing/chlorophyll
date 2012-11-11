#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys

import chlorophyll.gens as gens
import chlorophyll.template as template


def usage(msg):
    sys.stderr.write('Error: %s\n' % msg)
    # TODO: print usage


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage('wrong number of arguments')
        sys.exit(1)

    conf_file = sys.argv[1]
    execfile(conf_file)

    # check must-have configs defined?
    try:
        line_template
    except NameError:
        usage('no line_template configured in %s' % conf_file)
        sys.exit(1)

    try:
        line_number
    except NameError:
        usage('no line_number configured in %s' % conf_file)
        sys.exit(1)

    # check optional configs
    try:
        print header_template
    except NameError:
        pass


    tpl = template.Template(line_template)
    for line in tpl.render(line_number):
        print ''.join(str(_) for _ in line)
