import unittest
import os
import sys
sys.path.insert(0, os.path.abspath('./src'))
from http_message import basic_message

class TestBasicMessage(unittest.TestCase):
    def test_http_request_line_valid_method(self):
        req_line = basic_message.http_request_line('GET', '/the/path', '1.1')
        self.assertEqual(req_line, 'GET /the/path HTTP/1.1\r\n')

    def test_http_request_line_invalid_method(self):
        req_line = basic_message.http_request_line('FOO', '/the/path', '1.1')
        self.assertEqual(req_line, 'FOO /the/path HTTP/1.1\r\n')

    def test_http_request_line_version(self):
        req_line = basic_message.http_request_line('POST', '/the/path', '2.5')
        self.assertEqual(req_line, 'POST /the/path HTTP/2.5\r\n')

    def test_http_request_header(self):
        headers = basic_message.http_header_section({'Host': 'foo.com'})
        self.assertEqual(headers, 'Host: foo.com\r\n')

    def test_http_request_header_multiple(self):
        headers = basic_message.http_header_section({'Host': 'foo.com', 'TestHeader': 'testsession'})
        self.assertEqual(headers, 'Host: foo.com\r\nTestHeader: testsession\r\n')

    def test_http_body_section(self):
        body = basic_message.http_body_section('session=testsession')
        self.assertEqual(body, 'session=testsession')

    def test_required_headers_version_1_1(self):
        headers = basic_message.required_headers('1.1', 'foo.com')
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers, {'Accept': '*/*', 'Host': 'foo.com'})

    def test_required_headers_with_body(self):
        headers = basic_message.required_headers('1.2', 'foo.com', 'hello')
        self.assertIsInstance(headers, dict)
        self.assertEqual(headers, {'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded', 'Content-Length': 5})

    def test_create_http_message(self):
        message = basic_message.create_http_message('GET', 'http://foo.com', {'Session': 'testsession'})
        self.assertEqual(message, 'GET / HTTP/1.1\r\nAccept: */*\r\nHost: foo.com\r\nSession: testsession\r\n\r\n')

    def test_create_http_message_with_body(self):
        message = basic_message.create_http_message('GET', 'http://foo.com', {'Session': 'testsession'}, 'key=test')
        self.assertEqual(
            message,
            'GET / HTTP/1.1\r\nAccept: */*\r\n' \
            'Host: foo.com\r\n' \
            'Content-Type: application/x-www-form-urlencoded\r\n' \
            'Content-Length: 8\r\n' \
            'Session: testsession\r\n\r\n' \
            'key=test'
        )