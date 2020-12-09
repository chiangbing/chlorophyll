import unittest
import chlorophyll


class ChlorophyllTest(unittest.TestCase):

    def test_render_literals(self):
        ch = chlorophyll.Chlorophyll('"Literal:" "\\"0.1\\"" "0.1" "\n"  # line comment')
        result = next(ch.render(1))
        self.assertEqual(len(result), 4)
        self.assertEqual(result[0], 'Literal:')
        self.assertEqual(result[1], '"0.1"')
        self.assertEqual(result[2], '0.1')
        self.assertEqual(result[3], '\n')

    def test_url_gen(self):
        ch = chlorophyll.Chlorophyll('${=url}')
        result = next(ch.render(1))
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith('http://'))

    def test_anchor_and_ref(self):
        ch = chlorophyll.Chlorophyll('''
        ${uo=url}
        &uo
        ''')
        result = next(ch.render(1))
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], result[1])

    def test_builtin_funcs(self):
        ch = chlorophyll.Chlorophyll('${=hex(3)}')
        result = next(ch.render(1))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], hex(3))

    def test_custom_funcs(self):
        def my_len(s):
            return len(s)
        ch = chlorophyll.Chlorophyll('${=my_len("123")}', funcs=[my_len])
        result = next(ch.render(1))
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], 3)


if __name__ == '__main__':
    unittest.main()