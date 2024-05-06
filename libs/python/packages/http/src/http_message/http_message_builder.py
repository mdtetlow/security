import json
from abc import ABC, abstractmethod
from .request import HTTPRequest
import uuid

class AbstractHTTPMessageBuilder(ABC):
    @abstractmethod
    def set_header(self, key, value):
        pass

    @abstractmethod
    def set_body(self, body):
        pass

    @abstractmethod
    def add_multipart_body(self, headers, body):
        pass

    @abstractmethod
    def build(self):
        pass


class HTTPRequestBuilder(AbstractHTTPMessageBuilder):
    def __init__(self):
        super().__init__()
        self.request = {'method': 'GET', 'url': 'http://foo.com', 'version': '1.1'}
        self.headers = {}
        self.body = [] # single or multipart
    
    def set_request(self, method: str, url: str, version: str = '1.1'):
        self.request = {
            'method': method,
            'url': url,
            'version': version
        }

    def set_header(self, key, value):
        self.headers[key] = value
        return self
    
    def set_body(self, body):
        if isinstance(body, dict) and 'application/json' in self.headers.get('Content-Type', ''):
            self.body.append(json.dumps(body))
        elif isinstance(body, list):
            self.body.append('\r\n'.join(body))
        else:
            self.body.append(body)
        
        return self

    def add_multipart_body(self, headers, body = None):
        # add/update the required Content-Type Header
        header_values = ', '.join(self.headers.values())
        if not 'multipart/form-data' in header_values:
            self.headers['Content-Type'] = f"multipart/form-data; boundary=--{str(uuid.uuid4())}"
        elif not 'boundary=' in header_values:
            self.headers['Content-Type'] += f"; boundary=--{str(uuid.uuid4())}"

        self.body.append( (headers, body) )
        return self
    
    def build(self):
        return HTTPRequest(method = self.request.get('method'),
                           url = self.request.get('url'),
                           version = self.request.get('version'),
                           headers = self.headers,
                           body = self.body)

