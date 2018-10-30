#!/usr/local/bin/python3.6
import cgi
import json
import cgitb
import sys
import hmac
import os
import subprocess


def exit_on_error(e, MSG, eCode):
    global DataStorage
    DataStorage["Error"].append({"e": e, "msg": MSG, "error_code": eCode})
    choose_output()


def read_settings(file):
    try:
        f = open(file, 'r')
        return json.loads(f.read())
    except FileNotFoundError as e:
        exit_on_error(e, 'CONFIG FILE NOT FOUND', 404)


Settings = read_settings('config.json')
RawPayload = sys.stdin.read(int(os.environ["CONTENT_LENGTH"]))
DataStorage = {
    "Error": [],
    "X-GitHub-Delivery": os.environ["HTTP_X_GITHUB_DELIVERY"],
    "X-GitHub-Event": os.environ["HTTP_X_GITHUB_EVENT"],
    "X-Hub-Signature": os.environ["HTTP_X_HUB_SIGNATURE"],
    "User-Agent": os.environ["HTTP_USER_AGENT"],
    "Payload": json.loads(RawPayload),
    "OutputType": Settings['OutputType'],
    "Charset": Settings["Charset"],
    "Git": {
        "Status": {
            "Before": '',
            "After": ''
        }
    }
}


def process_output(Data):
    output = {
        "Error": Data['Error'],
        "Git": Data['Git'],
        "X-GitHub-Delivery": Data['X-GitHub-Delivery'],
        "X-GitHub-Event": Data['X-GitHub-Event'],
        "X-Hub-Signature": Data['X-Hub-Signature'],
        "User-Agent": Data['User-Agent'],
        "User": {
            "Name": Data['Payload']['sender']['login'],
            "Photo": Data['Payload']['sender']['avatar_url'],
            "URL": Data['Payload']['sender']['html_url'],
            "ID": Data['Payload']['sender']['id']
        },
        "Pusher": {
            "Name": Data['Payload']['pusher']['name'],
            "Email": Data['Payload']['pusher']['email']
        },
        "Repository": {
            "ID": Data['Payload']['repository']['id'],
            "Name": Data['Payload']['repository']['name'],
            "FullName": Data['Payload']['repository']['full_name'],
            "Private": Data['Payload']['repository']['private'],
            "URL": Data['Payload']['repository']['html_url'],
            "CloneURL": Data['Payload']['repository']['clone_url'],
            "GitURL": Data['Payload']['repository']['git_url'],
            "SSH_URL": Data['Payload']['repository']['ssh_url'],
            "SVN_URL": Data['Payload']['repository']['svn_url'],
            "Homepage": Data['Payload']['repository']['homepage'],
            "Description": Data['Payload']['repository']['description'],
            "Owner": {
                "Name": Data['Payload']['repository']['owner']['name'],
                "Email": Data['Payload']['repository']['owner']['email'],
                "Login": Data['Payload']['repository']['owner']['login'],
                "ID": Data['Payload']['repository']['owner']['id'],
                "Photo": Data['Payload']['repository']['owner']['avatar_url'],
                "URL": Data['Payload']['repository']['owner']['html_url']
            }
        },
        "ref": Data['Payload']['ref'],
        "LatestCommitID": Data['Payload']['after'],
        "Branch": Data['Payload']['ref'].rsplit('/', 1)[-1],
        "Compare": Data['Payload']['compare'],
        "Commits": Data['Payload']['commits']
    }
    return output


def git_status():
    out = {}
    s = subprocess.run('', stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, shell=True)
    for i in s.stdout.decode('utf-8').splitlines():
        out['STD']


def choose_output():
    Data = process_output(DataStorage)
    if (DataStorage["OutputType"] == "RAW"):
        output_as_raw(Data)
    elif (DataStorage["OutputType"] == "JSON"):
        output_as_json(Data)
    elif (DataStorage["OutputType"] == "HTML"):
        output_as_html(Data)
    elif (DataStorage["OutputType"] == "MARKDOWN"):
        output_as_markdown(Data)
    else:
        Data['Output']['Error'].append({"e": None, "msg": "OUTPUT TYPE '" +
                                        str(DataStorage["OutputType"]) + "' NOT SUPPORTED", "error_code": 501})
        output_as_json(Data)


def output_as_json(Data):
    print("Content-Type: application/json; charset=" +
          DataStorage["Charset"] + "\n\n")
    print(json.dumps(Data, indent=4, sort_keys=True))
    exit()


def output_as_raw(Data):
    print("Content-Type: text/plain; charset=" +
          DataStorage["Charset"] + "\n\n")
    exit()


def output_as_html(Data):
    print("Content-Type: text/html; charset=" +
          DataStorage["Charset"] + "\n\n")
    exit()


def output_as_markdown(Data):
    print("Content-Type: text/markdown; charset=" +
          DataStorage["Charset"] + "\n\n")
    exit()


def run():
    global DataStorage
    Algo, Hash = DataStorage['X-Hub-Signature'].split("=")
    PayloadHash = hmac.new(
        bytes(Settings['SECRET'], 'utf-8'), bytes(RawPayload, 'utf-8'), Algo).hexdigest()

    if (Hash != PayloadHash):
        exit_on_error(None, 'UNABLE TO VALIDATE PAYLOAD', 403)


run()
