#!/usr/bin/env python3
from http.message import create_http_message
from http.url import HTTPUrl
import argparse
import json
import sys
import socket

parser = argparse.ArgumentParser()
parser.add_argument('--url', help='HTTP URL', required=True)
parser.add_argument('--method', help='HTTP Method', default='GET')
parser.add_argument('--headers', help='HTTP Headers in JSON formatted string', required=False)
parser.add_argument('--body', help='HTTP Body', required=False)

args = parser.parse_args()
url = HTTPUrl(args.url)
body = args.body
headers = json.loads(args.headers) if args.headers else {}

message = create_http_message(method = args.method,
                                url = args.url,
                                headers = headers,
                                body = body)

print(f"\r\n{message}\r\n")

with socket.socket(family = socket.AF_INET,
                   type = socket.SOCK_STREAM) as s:
    s.connect(url.inet_address())
    s.sendall(str.encode(message))
    data = s.recv(1024)

print('received', repr(data))
