# -*- coding:utf-8 -*-

import gens.prims as prims
import gens.fs as fs
import gens.telecom as telecom
import gens.http as http
import template


tpl = template.template('urldb.chl')
tpl.bind('uo', http.url_gen())
tpl.bind('uu', http.url_gen())
tpl.bind('ro', http.url_gen())
tpl.bind('mod', prims.int_gen(min=0, max=2))
tpl.bind('dm', http.host_gen())
tpl.bind('dep', prims.int_gen(min=1, max=4))
tpl.bind('lan', prims.int_gen(min=0, max=2))
tpl.bind('wei', prims.int_gen(min=0, max=3))
tpl.bind('hub', prims.int_gen(min=0, max=3))
tpl.bind('bw', prims.int_gen(min=0, max=3))
tpl.bind('sr', prims.int_gen(min=0, max=3))
tpl.bind('del', prims.int_gen(min=0, max=2))

for line in tpl.render(10):
    print ''.join(str(_) for _ in line)
