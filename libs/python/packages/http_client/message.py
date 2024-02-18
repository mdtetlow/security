def http_request_line(action: str,
                      path: str,
                      version: str):
    return f"{action} {path} HTTP/{version}\r\n"

def http_header_section(headers: dict):
    return "\r\n".join(f'{k}: {v}' for k,v in headers.items()) + "\r\n"

def http_body_section(body: list):
    print(body)
    return "\r\n".join(body) + "\r\n"

def create_http_message(action: str,
                        path: str,
                        headers:dict = None,
                        body: list = None,
                        version: str = "1.1"):
    http_message = f"{http_request_line(action, path, version)}{http_header_section(headers)}\r\n"
    if body:
        print("Here")
        http_message = f"{http_message}{http_body_section(body)}"
    
    return http_message
