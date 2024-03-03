#!/usr/bin/env python3
from http import basic_message
import argparse
import socket

parser = argparse.ArgumentParser()
parser.add_argument('--host', required=True)
parser.add_argument('--port', type=int, default=80, required=False)

args = parser.parse_args()

message = message.create_http_message('GET',
                                      f"http://{args.host}/pentesterlab")

print(message)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((args.host, args.port))
    s.sendall(str.encode(message))
    data = s.recv(1024)

print('received', repr(data))
