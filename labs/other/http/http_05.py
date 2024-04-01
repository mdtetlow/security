#!/usr/bin/env python3
from http_message.http_message_builder import HTTPRequestBuilder
from http_message.url import HTTPUrl
import argparse
import socket

def socket_send(url: HTTPUrl, message: str):
    with socket.socket(family = socket.AF_INET,
                    type = socket.SOCK_STREAM) as s:
        s.connect(url.inet_address())
        s.sendall(str.encode(message))
        return s.recv(1024)

def message_send(method: str, url: str, headers: dict = None, body: str = None):
    builder = HTTPRequestBuilder()
    builder.set_request(method, url)
    if headers:
        for k, v in headers.items():
            builder.set_header(k, v)
        
    if body:
        builder.set_body(body)
    
    message = builder.build().message()
    print(message)

    return socket_send(HTTPUrl(url), message)

def lab_http_post_multipart_body(method, url):
    resp = message_send(method = method,
                        url = url,
                        headers = {'Content-Type': 'multipart/form-data'})
    print(resp)

"""
Create data structure containing Headers & Body for each Lab
Document in README file to include description of each lab including the generated message
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', help='HTTP URL', required=True)

    args = parser.parse_args()

    lab_http_post_multipart_body('POST', args.url)
