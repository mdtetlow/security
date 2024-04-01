"""HTML Message creation helper

Supports creating of RFC-9110 compliant HTTP Messages

RFC-9110: https://www.rfc-editor.org/rfc/rfc9110.html
Mozilla HTTP Messages: https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages
"""

from .url import HTTPUrl

def http_request_line(method: str,
                      path: str,
                      version: str) -> str:
    """Create HTTP Request Line format string

    Parameters
    ----------
    method : str
        HTTP method according to RFC-9110
        GET, PUT, HEAD, POST, DELETE, CONNECT, OPTIONS
    path : str
        HTTP resource path
    version : str
        HTTP version (1.1, 2.0, 3.0)
    """
    req_path = path if path else '/'

    return f"{method} {req_path} HTTP/{version}\r\n"

def http_header_section(headers: dict) -> str:
    """Creates HTTP Headers section (including Cookies) according to RFC-9110

    Parameters
    ----------
    headers : dict
        A dictionary object containing the Headers and Cookies as key,value pairs
    """

    return "\r\n".join(f'{k}: {v}' for k,v in headers.items()) + "\r\n"

def http_body_section(body: list):
    """Creates HTTP Body according to RFC-9110

    Parameters
    ----------
    body : list
        List of string lines making up the HTTP Body according to RFC-9110
    """

    return f"{body}"

def required_headers(version: str,
                     host: str,
                     body: str = None) -> str:
    headers: dict = {'Accept': '*/*'}

    if version == '1.1':
        headers.update({'Host': host})
    
    if body:
        headers.update(
            {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': len(body.encode('utf-8'))
            })

    return headers

def create_http_message(method: str,
                        url: str,
                        headers: dict = {},
                        body: str = None,
                        version: str = "1.1") -> str:
    """Create HTTP Message according to RFC-9110

    Parameters
    ----------
    method : str
        HTTP method according to RFC-9110
        GET, PUT, HEAD, POST, DELETE, CONNECT, OPTIONS
    path : str
        HTTP resource path
    headers : dict
        A dictionary object containing the Headers and Cookies as key,value pairs
    body : list
        List of string lines making up the HTTP Body according to RFC-9110
    version : str
        HTTP version (1.1, 2.0, 3.0)
    """
    url_obj = HTTPUrl(url)
    print(url_obj)
    request_line = http_request_line(method, url_obj.path(), version)
    headers_section = {**required_headers(version, url_obj.host(), body), **headers} # input argument headers overrides required headers values
    http_message = f"{request_line}{http_header_section(headers_section)}\r\n"
    if method == 'POST' or body:
        http_message = f"{http_message}{http_body_section(body)}"
    
    return http_message
