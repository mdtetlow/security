from copy import deepcopy
import numpy as np

class HTTPHeader:
    def __init__(self, name: str, value: str):
        self._name = name
        self._value = value
        self.directives = value.split(';') if isinstance(value, str) and ';' in value else None
    
    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        self._value = value
    
    def __getitem__(self, key):
        # print(f"Header.__getitem__() {key}")

        if not self.directives:
            raise AttributeError('Header has no directives')
        
        directive = ''
        if isinstance(key, int):
            # array index
            directive = self.directives[key]
        elif isinstance(key, str):
            # key value pair
            if key not in self.value:
                raise KeyError('Key not found in directives')
            
            val = ''
            for e in self.directives:
                if key == e:
                    val = e; break
                elif f"{key}=" in e:
                    val = e.split('=').pop().strip('\"'); break

            directive = val

        return directive

    def __eq__(self, other):
        return self.name.lower() == other.name.lower()
    
    def __hash__(self):
        return hash(self.name)
    
    def __len__(self):
        return 1 if not self.directives else len(self.directives)

    def __str__(self):
        return f"{self.name}: {self.value}"

class HTTPHeaderSection:
    def __init__(self, headers: dict = None):
        self.headers = []
        if headers:
            for name, value in headers.items():
                self.add_header(name, value)
    
    def add_header(self, name, value):
        header = HTTPHeader(name, value)
        if len([h for h in self.headers if h == header]) > 0:
            raise(AttributeError(f"Duplicate Header {header.name}"))
        
        self.headers.append(header)
    
    def get_header(self, name):
        header = None
        for h in self.headers:
            if name == h.name:
                header = h; break

        return header
    
    def update_header(self, name, value):
        header = self.get_header(name)
        for h in self.headers:
            if name == h.name:
                header = h; break

        return header
    
    def __iadd__(self, other):
        other_headers = deepcopy(other.headers)
        intersection = list(map(lambda header: header.name.lower(), set(self.headers) & set(other_headers)))
        for overwrite_header in [header for header in self.headers if header.name.lower() in intersection]:
            # print(str(overwrite_header))
            overwrite_header.value = [header for header in other_headers if header == overwrite_header].pop().value
            other_headers.remove(overwrite_header)
        
        self.headers.extend(other_headers)
        
        return self
    
    def __str__(self):
        headers = ''
        for header in self.headers:
            headers += f"{str(header)}\r\n"
        
        headers += '\r\n'
        return headers
