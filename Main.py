#!/usr/local/bin/python3.6
# import cgi
# import json
# import cgitb

import os

print("Content-Type: text/html")
print("Cache-Control: no-cache")
print()

print("<html><body><code>")
print(os.environ)
print("</code></html></body>")
