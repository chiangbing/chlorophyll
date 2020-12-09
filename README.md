Chlorophyll
===========

Chlorophyll is a utility for generating testing data.


Usage
-----

```python
import chlorophyll

# generate and print a list of random integers
ch = chlorophyll.Chlorophyll('${=int}')
for i in ch.render(100):
    print(i)
```

Template Grammar
----------------
`chlorophyll.Chrolophyll` receive a *template* as its first parameter, whose grammar is:

```
<expr> [expr...]
```

By invoking `chlorophyll.Chrolophyll.render`, the template will be rendered to a list of strings.

The supporting grammar of `expr` is:

<pre>
EXPRESSION                 OUPUT

"0.1"                      0.1
&uo                        http://vhosudhswg.biqdvijjoq.net/fwala/ckzklifl/qk_gv
${uo=url}                  http://vhosudhswg.biqdvijjoq.net/fwala/ckzklifl/qk_gv
&uo                        http://vhosudhswg.biqdvijjoq.net/fwala/ckzklifl/qk_gv
${=hex(3)}                 0x3
${=int("01010", base=2)    10
${=int}                    6012078762086482288
${=int(min=1, max=10)}     8
${=my_len(&uo)}            53

"0.1"                      0.1
&uo                        http://ryejufql.uqnwlyjfu.twhvyd.org/xplrryyk/heavoxic/qckdbekzqx
${uo=url}                  http://ryejufql.uqnwlyjfu.twhvyd.org/xplrryyk/heavoxic/qckdbekzqx
&uo                        http://ryejufql.uqnwlyjfu.twhvyd.org/xplrryyk/heavoxic/qckdbekzqx
${=hex(3)}                 0x3
${=int("01010", base=2)    10
${=int}                    7125728509514389461
${=int(min=1, max=10)}     4
${=my_len(&uo)}            65

"0.1"                      0.1
&uo                        http://xzgbx.cn/swfnwp/uh
${uo=url}                  http://xzgbx.cn/swfnwp/uh
&uo                        http://xzgbx.cn/swfnwp/uh
${=hex(3)}                 0x3
${=int("01010", base=2)    10
${=int}                    5556233375595097482
${=int(min=1, max=10)}     3
${=my_len(&uo)}            25
</pre>