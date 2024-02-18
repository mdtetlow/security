import argparse
import string
import json

base_headers = '{ \
  "Host": "", \
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0", \
  "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", \
  "Accept-Language": "en-GB,en;q=0.5", \
  "Accept-Encoding": "gzip, deflate", \
  "Referer": "", \
  "Upgrade-Insecure-Requests": "1", \
  "Sec-Fetch-Dest": "document", \
  "Sec-Fetch-Mode": "navigate", \
  "Sec-Fetch-Site": "same-origin", \
  "Sec-Fetch-User": "?1", \
  "Te": "trailers" \
}'

def args():
    # configure arguments
    parser = argparse.ArgumentParser(description='PortSwigger Blind SQLi')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--host', help='host address', required=True)
    # parser.add_argument('-c', '--cookies', help='cookies', required=True)
    parser.add_argument('-u', '--username', help='username', required=True)
    parser.add_argument('-p', '--password', help='password', required=True)
    parser.add_argument('-l', '--login', help='login api', default="/login")
    parser.add_argument('-f', '--file', help='password file', default="./passwords")
    
    return parser.parse_args()

def prepare_headers(headers):
    combined_headers = None
    try:
        h1 = json.loads(base_headers)
        h2 = json.loads(headers)
        combined_headers = {**h1, **h2}
    except json.decoder.JSONDecodeError:
        print("ERROR: invalid headers format")
        pass
    
    return json.dumps(combined_headers)