#!/usr/bin/env python3

def construct_js_command(cmd: str, args: str):
    charCodes = list(map(ord, args))
    return f"{cmd}({','.join(map(str, charCodes))})"