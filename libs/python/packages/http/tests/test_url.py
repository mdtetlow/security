import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('./src'))
from http_message import url

class TestHTTPUrl(unittest.TestCase):
    def test_url_port_is_number(self):
        url_obj = url.HTTPUrl('https://foo.com')
        self.assertIsInstance(url_obj.port(), int)
    
    def test_url_port_secure(self):
        url_obj = url.HTTPUrl('https://foo.com')
        self.assertEqual(url_obj.port(), 443)

    def test_url_port_insecure(self):
        url_obj = url.HTTPUrl('http://foo.com')
        self.assertEqual(url_obj.port(), 80)

    def test_url_port_specified(self):
        url_obj = url.HTTPUrl('http://foo.com:9090')
        self.assertEqual(url_obj.port(), 9090)

    def test_url_port_host(self):
        url_obj = url.HTTPUrl('http://foo.com')
        self.assertEqual(url_obj.host(), 'foo.com')

    def test_url_port_path_empty(self):
        url_obj = url.HTTPUrl('http://foo.com')
        self.assertEqual(url_obj.path(), '')

    def test_url_port_path(self):
        url_obj = url.HTTPUrl('http://foo.com/one/two')
        self.assertEqual(url_obj.path(), '/one/two')

    def test_url_port_query_empty(self):
        url_obj = url.HTTPUrl('http://foo.com')
        self.assertEqual(url_obj.path(), '')

    def test_url_port_query(self):
        url_obj = url.HTTPUrl('http://foo.com?foo=bar&new=old')
        self.assertEqual(url_obj.path(), '?foo=bar&new=old')

    def test_url_port_inet(self):
        url_obj = url.HTTPUrl('http://foo.com')
        self.assertEqual(url_obj.inet_address(), ('foo.com', 80))
