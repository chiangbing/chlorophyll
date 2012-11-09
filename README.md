Chloriphyll
===========

By Clay Chiang (chiangbing@gmail.com)


Description
-----------

Chlorophyll is a utility for generating test data.


Template Grammar
----------------

1, Literal:     '"'
                "hello world" (including the quote)
2, Variable:     ${name}
3, Evaluation:   ${name=func(arg1, arg2, arg3)}, name and arg list is optional

4, Reference:    #name