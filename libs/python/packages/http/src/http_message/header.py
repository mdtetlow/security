class HTTPHeader:
    def __init__(self, name: str, value: str):
        self._name = name
        self._value = value
        self.directives = value.split(';') if ';' in value else None
    
    @property
    def name(self):
        return self._name
    
    @property
    def value(self):
        return self._value
    
    def __getitem__(self, key):
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
    
    def __len__(self):
        return 1 if not self.directives else len(self.directives)

    def __str__(self):
        return f"{self.name}: {self.value}"