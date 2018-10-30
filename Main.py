#!/usr/local/bin/python3.6
import cgi
import json
import cgitb
import sys
import hmac
import os
import subprocess


class cd:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def exit_on_error(e, MSG, eCode):
    global DataStorage
    DataStorage["Error"].append({"e": e, "msg": MSG, "error_code": eCode})
    choose_output(DataStorage)


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
    "Branch": DataStorage['Payload']['ref'].rsplit('/', 1)[-1],
}


def process_output(Data):
    output = {
        "Error": DataStorage['Error'],
        "X-GitHub-Delivery": DataStorage['X-GitHub-Delivery'],
        "X-GitHub-Event": DataStorage['X-GitHub-Event'],
        "X-Hub-Signature": DataStorage['X-Hub-Signature'],
        "User-Agent": DataStorage['User-Agent'],
        "ref": DataStorage['Payload']['ref'],
        "LatestCommitID": DataStorage['Payload']['after'],
        "Branch": DataStorage['Branch'],
        "Compare": DataStorage['Payload']['compare'],
        "Commits": DataStorage['Payload']['commits'],
        "Commands": Data
    }
    return output


# def git_status():
#     out = {
#         "STDOUT": [],
#         "STDERR": []
#     }
#     s = subprocess.run('git status -vv --long', stdout=subprocess.PIPE,
#                        stderr=subprocess.PIPE, shell=True)
#     for i in s.stdout.decode('utf-8').splitlines():
#         out['STDOUT'].append(str(i))
#     for i in s.stderr.decode('utf-8').splitlines():
#         out['STDERR'].append(str(i))
#     return out


# def git_reset():
#     out = {
#         "STDOUT": [],
#         "STDERR": []
#     }
#     s = subprocess.run('git reset --hard', stdout=subprocess.PIPE,
#                        stderr=subprocess.PIPE, shell=True)
#     for i in s.stdout.decode('utf-8').splitlines():
#         out['STDOUT'].append(str(i))
#     for i in s.stderr.decode('utf-8').splitlines():
#         out['STDERR'].append(str(i))
#     return out


def choose_output(Data):
    Data = process_output(Data)
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

    out = {}

    if (DataStorage['Payload']['repository']['name'] in Settings['Repositories'] or DataStorage['Payload']['repository']['full_name'] in Settings['Repositories']):
        pass
    else:
        exit_on_error('', "NO CONFIGURATION FOR REPOSITORY", 404)

    # with cd()

    # DataStorage['Git']['Status']['Before'] = git_status()

    # DataStorage['Git']['Status']['After'] = git_status()

    choose_output(out)


run()
