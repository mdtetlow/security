from .url import HTTPUrl
from .header import HTTPHeader, HTTPHeaderSection
from .body import HTTPBodySingleResource, HTTPBodyMultipleResource
import socket

class HTTPRequest:
    def __init__(self, 
                 method: str,
                 url: str,
                 version: str,
                 headers: dict,
                 body: list):
        self.url = HTTPUrl(url)
        self.method = method
        self.version = version
        self.header_section = self.__mandatory_headers()
        self.header_section += HTTPHeaderSection(headers)
        self.body = self.__setup_body(body) if body else None
        self.request_line = lambda: f"{self.method} {self.url.path()} HTTP/{self.version}\r\n"

    # @property
    # def headers(self):
    #     return self.header_section
    
    # @property
    # def body(self):
    #     return self.body
    
    def send(self) -> str:
        resp = None
        sock = None
        request_message = self.request_line() + self.__prepare_headers()
        if isinstance(self.body, HTTPBodySingleResource):
            request_message += self.body
            print(request_message)
            sock, resp = self.__socket_send(self.url, request_message)
        elif isinstance(self.body, HTTPBodyMultipleResource):
            print(request_message, end='')
            sock, resp = self.__socket_send(self.url, request_message, resp = False)
            print(str(self.body))
            sock, resp = self.__socket_send(self.url, str(self.body), sock = sock)
        else:
            raise ValueError('Invalid HTTP Body Type')
            
        return resp
    
    def __socket_send(self, url: HTTPUrl, message: str, resp: bool = True, sock = None):
        s = sock
        r = None
        if not s:
            s = socket.socket(family = socket.AF_INET, type = socket.SOCK_STREAM)
            s.connect(url.inet_address())
        
        size = s.send(str.encode(message))
        print(f"sent {size} bytes")
        if resp:
            r = s.recv(1024)
        
        return s, r
    
    def __setup_body(self, body):
        _body = None
        # multipart body
        if isinstance(body, list) and isinstance(body[0], tuple):
            boundary = None
            content_type_header = self.header_section.get_header('Content-Type')
            if content_type_header:
                try:
                    boundary = content_type_header['boundary']
                except AttributeError:
                    print('Exception: boundary not set in Content-Type Header')
                    pass

            bodies = body if isinstance(body, list) else [body] # convert to list if tuple
            _body = HTTPBodyMultipleResource(boundary)
            for h, b in body:
                _body.add_body_part(
                    header_section = HTTPHeaderSection(h),
                    body = b
                )
        # single resource body
        elif isinstance(body, list) and len(body) == 1 or isinstance(body, str):
            body_str = body.pop() if isinstance(body, list) else body
            _body = HTTPBodySingleResource(body_str)
        else:
            raise TypeError('Invalid body type')
        
        return _body
    
    def __mandatory_headers(self):
        headers = HTTPHeaderSection()
        if self.version == '1.1':
            headers.add_header('Host', self.url.host())

        headers.add_header('Accept', '*/*')
        return headers
    
    # def __prepare_message(self):
    #     # add Content-Length Header if necessary
    #     if self.method in ['POST', 'PUT'] and \
    #        isinstance(self.body, HTTPBodySingleResource) or isinstance(self.body, HTTPBodyMultipleResource) and not \
    #        self.header_section.get_header('Content-Length'):
    #         self.header_section.add_header('Content-Length', len(self.body))
        
    #     return f"{self.method} {self.url.path()} HTTP/{self.version}\r\n" \
    #            f"{str(self.header_section)}" \
    #            f"{str(self.body)}"
    
    def __prepare_headers(self):
        # add Content-Length Header if necessary
        if self.method in ['POST', 'PUT'] and \
           not self.header_section.get_header('Content-Length'):
            self.header_section.add_header('Content-Length', len(self.body))
        
        return str(self.header_section)

    
    # def __str__(self):
    #     return self.__prepare_message()
