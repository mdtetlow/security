#!/usr/bin/env python3
import hashlib
import requests

def password_sha1(password):
  passwd_sha1 = hashlib.sha1(password.encode())
  return passwd_sha1.hexdigest()

def verify_password(hash):
    prefix = hash[0:5]
    print("password prefix: {}".format(prefix))
    resp = requests.get("https://api.pwnedpasswords.com/range/{}".format(prefix))
    return resp.status_code, resp.text


if __name__ == '__main__':
    print('main')
    hash = password_sha1('password')
    print("hash: {}".format(hash))
    code, data = verify_password(hash)
    print(code)
    print(data)
