# Vulnerabilities Identified

The application used string formatting to build SQL queries in both the /search and /transaction endpoints.

User-provided input (such as username, user ID, or amount) was directly inserted into SQL statements without proper validation.

This created a SQL Injection vulnerability, where an attacker could modify the SQL query by sending malicious input.

Through SQL Injection, an attacker could:

Access unauthorized user records

Bypass intended query conditions

Manipulate or corrupt financial data such as user balances

This issue is critical because it compromises data confidentiality, integrity, and security.

The vulnerability was fixed by using parameterized queries, ensuring user input is treated strictly as data and not executable SQL.



# Performance Solution Chosen

The /transaction endpoint simulated a slow external banking service using time.sleep().

Flask processes requests synchronously, so this delay blocked the worker thread handling the request.

When multiple users triggered transactions, the application became unresponsive or appeared frozen.

To solve this, the transaction logic was moved to a background thread using Python’s threading module.

# The API now:

Immediately responds to the client

Continues processing the transaction asynchronously in the background

Threading was chosen because:

It is simple and lightweight

It does not require changing the web framework

It fits well within the project’s time and complexity constraints

This approach ensures the application remains responsive under concurrent requests.
