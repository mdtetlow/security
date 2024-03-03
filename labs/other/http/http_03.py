#!/usr/bin/env python3
from http import basic_message
import sys
import socket
from urllib.parse import urlparse

def port(url):
    port: int = -1
    parts = url.netloc.split(':')
    if len(parts) == 2:
        port = parts[1]
    else:
        port = 80 if url.scheme == 'http' else 443
    
    return int(port)

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} [url]")
    exit(2)

url = urlparse(sys.argv[1])

message = message.create_http_message(method = 'GET',
                                      url = sys.argv[1],
                                      headers = {'Host': url.netloc, 'Cookie': 'key=please'})

print(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((url.netloc, port(url)))
    s.sendall(str.encode(message))
    data = s.recv(1024)

print('received', repr(data))
