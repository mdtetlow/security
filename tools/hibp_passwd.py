#!/usr/bin/env python3

# HIBP (have I been pwned) Password API wrapper CLI tool
#
# Overview:
# Only the first 5 digits of the password Hash (SHA1) are passed to the API (HTTPS).
# The API returns a list of SHA1 password Hashes (Hash minus first 5 digits) from
# the leaked password databases that share the same 5 digit Hash prefix.
# The list (0..*) is searched locally for matches.
#
# Usage $> hibp_passwd.py <plaintext password>
# Returns:
#   -1: HTTP API error
#    0: Password has not been identified in the leaked password data sources
#    N: Password has been leaked - positive number representing prevalance count

import hashlib
import re
import requests
import sys

HASH_PREFIX_SIZE = 5
HTTP_STATUS_SUCCESS = 200
API= 'https://api.pwnedpasswords.com/range'

hash_prefix = lambda h : h[0:HASH_PREFIX_SIZE]
hash_suffix = lambda h : h[HASH_PREFIX_SIZE:]

def usage():
  print("Usage: {} <plaintext password>".format(sys.argv[0]))
  exit(1)

def password_sha1(plaintext_password):
  passwd_sha1 = hashlib.sha1(plaintext_password.encode())
  return passwd_sha1.hexdigest().upper()

def password_leaked(passwd_sha1):
  http_status, data = invoke_api(passwd_sha1)
  count = 0

  if http_status != HTTP_STATUS_SUCCESS:
    return -1
  
  m1 = re.search(r"{}".format(hash_suffix(passwd_sha1)), data)
  if m1:
    data_remaining = data[m1.end():m1.end()+30]
    m2 = re.search(r'\d.*', data_remaining)
    count = int(data_remaining[m2.start():m2.end()])
  
  return count

def invoke_api(passwd_sha1):
  prefix = passwd_sha1[0:5]
  resp = requests.get("{}/{}".format(API, prefix))
  return resp.status_code, resp.text

if __name__ == '__main__':
  if len(sys.argv) != 2:
    usage()

  passwd_sha1 = password_sha1(str(sys.argv[1]))
  count = password_leaked(passwd_sha1)
  print(count)
  