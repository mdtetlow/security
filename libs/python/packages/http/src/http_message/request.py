from .url import HTTPUrl
import uuid

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
        self.headers = {**self.mandatory_headers(), **headers}
        self.body = body
        self.multi_part_boundary = f"--{uuid.uuid4().hex}"

    def mandatory_headers(self):
        headers = {}
        if self.version == '1.1':
            headers['Host'] = self.url.host()
        
        headers['Accept'] = '*/*'
        return headers
    
    def __prepare_headers(self, headers: dict):
        headers_str = ''
        content_type = headers.get('Content-Type')
        if content_type and content_type.find('multipart/form-data') >= 0:
            if content_type.find('boundary=') >= 0:
                self.multi_part_boundary = content_type.split('boundary=').pop()
            else:
                headers['Content-Type'] += f"; boundary={self.multi_part_boundary}"
        
        for k, v in headers.items():
            headers_str += f"{k}: {v}\r\n"
        
        headers_str += '\r\n'
        return headers_str
    
    def __prepare_singlepart_body(self):
        return '\r\n'.join(self.body)

    def __read_file(self, mime_type: str, file: str):
        print(f"mime: {mime_type} {file}")

    def __prepare_multipart_body(self):
        body = ''

        if not self.body:
            return body
        
        print(self.body)
        for headers, body_part in self.body:
            content_disposition_header = headers.get('Content-Disposition')
            file_contents = None
            if content_disposition_header and 'filename=' in content_disposition_header:
                params = content_disposition_header.split(';')
                file_contents = self.__read_file(mime_type = '', file = '')
            body += f"{self.multi_part_boundary}\r\n"
            body += self.__prepare_headers(headers)
            body += f"{body_part}\r\n"
        
        body += f"{self.multi_part_boundary}--\r\n"
        return body
    
    def __prepare_message(self):
        message = f"{self.method} {self.url.path()} HTTP/{self.version}\r\n" \
                  f"{self.__prepare_headers(self.headers)}"
        if self.headers.get('Content-Type') and self.headers['Content-Type'].find('multipart/form-data') != -1:
            message += self.__prepare_multipart_body()
        else:
            message += self.__prepare_singlepart_body()

        return message
    
    def message(self):
        return self.__prepare_message()
    
    def __str__(self):
        return self.message()