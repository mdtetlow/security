#!/usr/bin/env python3
from http_client import message
import argparse
import socket

parser = argparse.ArgumentParser()
parser.add_argument('--host', help='Hostname excluding protocal', required=True)
parser.add_argument('--port', type=int, default=80, required=False)

args = parser.parse_args()

message = message.create_http_message('GET',
                                           f"http://{args.host}/pentesterlab",
                                           {'Host': args.host})

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((args.host, args.port))
    s.sendall(str.encode(message))
    data = s.recv(1024)

print('received', repr(data))
