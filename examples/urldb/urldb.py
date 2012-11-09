# -*- coding:utf-8 -*-

import sys

sys.path.append('../../')

import chlorophyll.gens as gens
import chlorophyll.template as template


tpl = template.Template('urldb.chl')
tpl.bind('uo', gens.url_gen())
tpl.bind('uu', gens.url_gen())
tpl.bind('ro', gens.url_gen())
tpl.bind('mod', gens.int_gen(min=0, max=2))
tpl.bind('dm', gens.host_gen())
tpl.bind('dep', gens.int_gen(min=1, max=4))
tpl.bind('lan', gens.int_gen(min=0, max=2))
tpl.bind('wei', gens.int_gen(min=0, max=3))
tpl.bind('hub', gens.int_gen(min=0, max=3))
tpl.bind('bw', gens.int_gen(min=0, max=3))
tpl.bind('sr', gens.int_gen(min=0, max=3))
tpl.bind('del', gens.int_gen(min=0, max=2))

for line in tpl.render(10):
    print ''.join(str(_) for _ in line)
