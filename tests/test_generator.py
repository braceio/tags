import unittest
import os
import shutil
from filecmp import dircmp
 
from tags.utils import *
from tags import generator


class TestTemplateLanguage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        wwwroot = os.path.dirname(os.path.realpath(__file__))+"/www"
        cls.cwd = os.getcwd()
        os.chdir(wwwroot)
        shutil.rmtree(os.path.join(wwwroot, "_site"), ignore_errors=True)


    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.cwd)


    def test_build_file(self):
        generator.build_file('index.html', "_site/index.html")
        self.assertEqual(dircmp('_gen_result_1', '_site').diff_files, [])


    def test_build_files(self):
        generator.build_files()
        self.assertEqual(dircmp('_gen_result_2', '_site').diff_files, [])


if __name__ == '__main__':
    unittest.main()