import unittest
import os
import sys

from tags.templatelang import TemplateLanguage

def _testfile(name):
    root = os.path.dirname(os.path.realpath(__file__))
    return open(root+'/'+name)

class TestTemplateLanguage(unittest.TestCase):

    def setUp(self):

        def _test(*args, **kwargs):
            args = list(args)
            body = kwargs.pop('body','')
            if body:
                args.append(body)
            return ', '.join(args)

        self.lang = TemplateLanguage(tags={'t': _test}, development=True)

        self.unicodedata = []
        for line in _testfile("unicodedata.txt"):
            if sys.version > '3':
                test, result = str(line).split(' --> ')
            else:
                test, result = unicode(line, 'utf-8').split(' --> ')
            self.unicodedata.append({
                'test': test.strip(), 
                'result': result.strip()
            })


    def test_tags(self):
        result = self.lang.parse("hello {% t world %}")
        self.assertEqual(result, "hello world")
        result = self.lang.parse("hello {%t world%}")
        self.assertEqual(result, "hello world")
        result = self.lang.parse("hello {%t world yeah %}")
        self.assertEqual(result, "hello world, yeah")
        result = self.lang.parse("hello {%t 'big world' %}")
        self.assertEqual(result, "hello big world")
        result = self.lang.parse("hello {%t 'big world' uh... %}")
        self.assertEqual(result, "hello big world, uh...")
        result = self.lang.parse(self.unicodedata[0]['test'])
        self.assertEqual(result, self.unicodedata[0]['result'])


    def test_block_tag(self):
        result = self.lang.parse("hello {% t %}world{% endt %}")
        self.assertEqual(result, "hello world")
        result = self.lang.parse("hello {%t%}world{%endt%}")
        self.assertEqual(result, "hello world")
        result = self.lang.parse("hello {% t%}world{%endt %}")
        self.assertEqual(result, "hello world")
        result = self.lang.parse("hello {% t oh my %}world{%endt %}")
        self.assertEqual(result, "hello oh, my, world")
        result = self.lang.parse(self.unicodedata[1]['test'])
        self.assertEqual(result, self.unicodedata[1]['result'])


    def test_tag_list(self):
        result = self.lang.parse("{%t hello%} {%t world%}")
        self.assertEqual(result, "hello world")


    def test_block_list(self):
        result = self.lang.parse("{%t%}hello{%endt%} {%t%}world{%endt%}")
        self.assertEqual(result, "hello world")


    def test_invalid_tag(self):
        result = self.lang.parse("hello {% bad %}world{% endbad %}")
        self.assertEqual(result, "hello {% bad %}world{% endbad %}")
        result = self.lang.parse("hello {% tbad %}world{% endtbad %}")
        self.assertEqual(result, "hello {% tbad %}world{% endtbad %}")


    def test_nested_blocks(self):
        teststr = '{%t l1 %}hello {%t l2 %}world {%endt%}/l1{%endt%}'
        self.assertEqual(self.lang.parse(teststr), "l1, hello l2, world /l1")
        teststr = '{%t%}{%t%}hello {%endt%}{%t%}nested {%t%}world{%endt%}{%endt%}{%endt%}'
        self.assertEqual(self.lang.parse(teststr), "hello nested world")


if __name__ == '__main__':
    unittest.main()
