# Chlorophyll template examples( this is a comment)

# {{{ configurations

#
header_template = '''
 TYPE                               EXPRESSION                 OUPUT
 ----                               -----------                -----'''

line_template = '''
" Literal:                           "   "\\"0.1\\"                      " "0.1"                           "\n"  # This is another comment
" Reference 1:                       "   "&uo                        " &uo                             "\n"
" Builtin Gens:                      "   "${uo=url}                  " ${uo=url}                       "\n"
" Reference 2:                       "   "&uo                        " &uo                             "\n"
" Builtin Function 1:                "   "${=hex(3)}                 " ${=hex(3)}                      "\n"
" Builtin Function 2:                "   "${=int(\\"01010\\", base=2)    " ${=int("01010", base=2)}        "\n"
" Builtin Gens 2:                    "   "${=int}                    " ${=int}                         "\n"
" Builtin Gens 3:                    "   "${=int(min=1, max=10)}     " ${=int(min=1, max=10)}          "\n"
'''

line_number = 3

# }}}

# Custom functions
# TODO
