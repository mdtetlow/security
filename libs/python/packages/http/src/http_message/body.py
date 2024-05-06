from abc import ABC, abstractmethod
from .header import HTTPHeader, HTTPHeaderSection
import uuid

class AbstractHTTPBody(ABC):
    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def prepare_body(self):
        pass

    def __str__(self):
        return self.prepare_body()

class HTTPBodySingleResource(AbstractHTTPBody):
    def __init__(self, body: str = None):
        super().__init__()
        self.body = body
    
    def __len__(self) -> int:
        return len(self.body.encode('utf-8'))

    def prepare_body(self):
        return f"{self.body}\r\n"

class HTTPBodyMultipleResource(AbstractHTTPBody):
    def __init__(self, boundary: str):
        super().__init__()
        self.boundary = boundary
        self.body = []
        self.body_formated = ''
    
    def add_body_part(self, header_section: HTTPHeaderSection, body = None):
        self.body.append( (header_section, body) )
    
    def __len__(self) -> int:
        if len(self.body_formated) == 0:
            self.body_formated = self.prepare_body()
        
        # print(f"len({self.body_formated.encode('utf-8')})")
        return len(self.body_formated.encode('utf-8'))

    def prepare_body(self):
        body_str = self.body_formated
        
        if body_str:
            return body_str
        
        for headers, body in self.body:
            _body = body
            # load file into body if specified
            if headers and 'filename=' in str(headers):
                _body = self.__load_file(headers.get_header('Content-Disposition'))
            
            # construct body
            body_str += f"--{self.boundary}\r\n"
            body_str += str(headers)
            body_str += f"{str(_body)}\r\n"
        
        body_str += f"--{self.boundary}--"

        return body_str

    def __load_file(self, header: HTTPHeader)-> str:
        body = ''
        file = header['filename'] # can raise exception
        # print(file)
        with open(file) as reader:
            body = reader.read().rstrip()
            body += '\r\n'

        # print(body)

        return body
