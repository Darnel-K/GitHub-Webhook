#!/usr/local/bin/python3.6
import cgi
import json
import cgitb
import sys
import hmac
import os

try:
    f = open('config.json', 'r')
    Settings = json.loads(f.read())
except FileNotFoundError as e:
    print("Content-Type: text/plain; charset=utf-8\n\nERROR: CONFIG FILE NOT FOUND")
    exit()

Payload = sys.stdin.read(int(os.environ["CONTENT_LENGTH"]))
Data = {
    "X-GitHub-Delivery": os.environ["HTTP_X_GITHUB_DELIVERY"],
    "X-GitHub-Event": os.environ["HTTP_X_GITHUB_EVENT"],
    "X-Hub-Signature": os.environ["HTTP_X_HUB_SIGNATURE"],
    "User-Agent": os.environ["HTTP_USER_AGENT"],
    "Payload": json.loads(Payload)
}

Hash_Algo = Data['X-Hub-Signature'].split("=")
PayloadHash = hmac.new(
    bytes(Hash_Algo[1], 'utf-8'), bytes(Payload, 'utf-8'), Hash_Algo[0])

print("Content-Type: application/json; charset=utf-8\n\n")

print(json.dumps(Data, indent=4))
print(PayloadHash)
