#!/usr/bin/env python
import os, os.path
import hmac
import hashlib
import json
import subprocess
from flask import Flask, request, redirect, abort, Response
app = Flask(__name__)

PROJECTS_ROOT = '/var/www'
FUNNEL_STAGING_TOUCHFILE = '/tmp/stagingreload'
WEBHOOK_SECRET = ''  # define webhook secret in local_settings.py

try:
    from local_settings import *
except ImportError as e:
    print "Local settings not found, no secret will be checked"


@app.route('/')
def index():
    return redirect('https://github.com/hasgeek')


@app.route('/', methods=['POST'])
def commit():
    request_data = request.get_data()
    signature = 'sha1=' + hmac.new(WEBHOOK_SECRET, request_data, hashlib.sha1).hexdigest()
    if 'X-Hub-Signature' not in request.headers or request.headers.get('X-Hub-Signature') != signature:
        return "Signature doesn't match", 401

    if not request.headers.get('X-GitHub-Event') == 'push':
        return "Only push events are allowed", 401

    payload = request.form.get('payload')
    if not payload:
        return "Missing form variable 'payload'"

    payload = json.loads(payload)
    reponame = payload['repository']['name']
    savedir = os.getcwd()
    repodir = os.path.join(PROJECTS_ROOT, reponame, 'staging')  # will fail for hgtv

    if reponame == 'funnel':
        os.chdir(repodir)
        current_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], env=os.environ).rstrip('\n')
        if 'ref' in payload and payload['ref'] == "refs/heads/{staging_branch}".format(staging_branch=current_branch):
            if os.access(repodir, os.W_OK | os.X_OK):
                pull_output = subprocess.check_output(['git', 'pull', 'origin', current_branch], env=os.environ)  # if failed, it'll raise exception

                os.chdir(savedir)  # Is this really required?
                return pull_output
    else:
        return "Unknown repository, or no access", 401


application = app  # For WSGI


if __name__ == '__main__':
    app.run('0.0.0.0')
