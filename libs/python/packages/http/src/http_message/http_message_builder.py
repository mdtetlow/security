import json
import uuid
from abc import ABC, abstractmethod

class AbstractHTTPMessageBuilder(ABC):
    @abstractmethod
    def set_header(self, key, value):
        pass

    @abstractmethod
    def set_body(self, body):
        pass

    @abstractmethod
    def add_body_part(self, headers, body):
        pass

    @abstractmethod
    def build(self):
        pass


class HTTPRequestBuilder(AbstractHTTPMessageBuilder):
    def __init__(self):
        self.headers = {}
        self.body = [] # single or multipart
        self.multi_part_boundary = f"Boundary{uuid.uuid4().hex}"

        def set_header(self, key, value):
            self.headers[key] = value
            return self
        
        def set_body(self, body):
            if isinstance(body, dict) and "application/json" in self.headers.get("Content-Type", ""):
                self.body = json.dumps(body)
            else:
                self.body = body

            return self


class HTTPRequest:
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body

    def __str__(self):
        
        
