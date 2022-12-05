#!/usr/bin/env python3
import hashlib
import requests
import sys

def password_sha1(plaintext_password):
  passwd_sha1 = hashlib.sha1(plaintext_password.encode())
  return passwd_sha1.hexdigest()

def verify_password(passwd_sha1):
  prefix = passwd_sha1[0:5]
  print("password prefix: {}".format(prefix))
  resp = requests.get("https://api.pwnedpasswords.com/range/{}".format(prefix))
  return resp.status_code, resp.text

def usage():
  print("Usage: {} <plaintext password>".format(sys.argv[0]))
  exit(1)

if __name__ == '__main__':
  if len(sys.argv) != 2:
    usage()

  password = str(sys.argv[1])
  passwd_sha1 = password_sha1(password)
  print("passwd_sha1: {}".format(passwd_sha1))
  code, data = verify_password(passwd_sha1)
  print(code)
  print(data)
