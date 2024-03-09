"""HTTP URL helper
"""

from urllib.parse import urlparse

class HTTPUrl:

    def __init__(self, url: str):
        self.url = urlparse(url)

    def __str__(self) -> str:
        return f""
    
    def inet_address(self):
        return self.__inet_address_from_url()
    
    def port(self):
        # get inet_addr tuple (host,port)
        addr = self.__inet_address_from_url()
        return addr[1]
    
    def host(self):
        return self.url.netloc.split(':')[0] # extract host from [host:port]
    
    def path(self):
        path = self.url.path + f"?{self.url.query}" if self.url.query else self.url.path
        return path
    
    def query(self):
        return self.url.query
    
    # private methods
    def __inet_address_from_url(self):
        """Socket AF_INET Address from HTTP URL

        Parameters
        ----------
        url : str
            HTTP format URL
        """
        port: int = self.url.port

        if not port:
            port = 80 if self.url.scheme == 'http' else 443
        
        return (self.host(), port)