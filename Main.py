#!/usr/local/bin/python3.6
import cgi
import json
import cgitb
import sys

import os
Data = {
    "X-GitHub-Delivery": os.environ["HTTP_X_GITHUB_DELIVERY"],
    "X-GitHub-Event": os.environ["HTTP_X_GITHUB_EVENT"],
    "X-Hub-Signature": os.environ["HTTP_X_HUB_SIGNATURE"],
    "User-Agent": os.environ["HTTP_USER_AGENT"],
    "Payload": json.loads(sys.stdin.read(int(os.environ["CONTENT_LENGTH"])))
}

print("Content-Type: application/json; charset=utf-8\n\n")

print(json.dumps(Data, indent=4))
