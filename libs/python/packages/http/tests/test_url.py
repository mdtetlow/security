import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('./src'))
from http_message import url

class TestHTTPMessageUrl(unittest.TestCase):
    def test_url(self):
        self.assertTrue(True)

# if __name__ == '__main__':
#     unittest.main()