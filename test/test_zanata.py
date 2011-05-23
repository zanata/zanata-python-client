'''
Created on May 20, 2011

@author: jamesni
'''
import unittest
import sys, os
sys.path.insert(0, os.path.abspath(__file__+"/../.."))

from zanataclient import zanata


class ZanataTest(unittest.TestCase):
    def setup(self):
        pass

    def test_convert_serverversion(self):
        server_version = "1.3.3"
        version_number = zanata.convert_serverversion(server_version)
        self.assertEqual(version_number, 1.3)

    def test_seachfile(self):
        path = "./po"
        result = zanata.search_file(path, "test.po")
        self.assertEqual(result, "./po/test.po")

if __name__ == '__main__':
    unittest.main()
    