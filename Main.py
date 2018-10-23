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

Algo, Hash = Data['X-Hub-Signature'].split("=")
PayloadHash = hmac.new(
    bytes(Settings['SECRET'], 'utf-8'), bytes(Payload, 'utf-8'), Algo).hexdigest()

if (Hash != PayloadHash):
    print("Content-Type: text/plain; charset=utf-8\n\nERROR: UNABLE TO VALIDATE REQUEST")
    exit()

print("Content-Type: application/json; charset=utf-8\n\n")

print(json.dumps(Data, indent=4))
