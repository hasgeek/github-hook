#!/usr/bin/env python
import os, os.path
import json
import subprocess
from flask import Flask, request, redirect, abort
app = Flask(__name__)

PROJECTS_ROOT = '/var/www'
FUNNEL_STAGING_BRANCH = 'staging'  # we only need this for funnel right now
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
    payload = request.form.get('payload')
    if not payload:
        return "Missing form variable 'payload'"
    payload = json.loads(payload)
    print payload
    reponame = payload['repository']['name']
    savedir = os.getcwd()
    repodir = os.path.join(PROJECTS_ROOT, reponame, reponame)  # will fail for hgtv

    if reponame == 'funnel':
        if payload['ref'] == "refs/heads/{staging_branch}".format(staging_branch=FUNNEL_STAGING_BRANCH):
            if os.access(repodir, os.W_OK | os.X_OK):
                os.chdir(repodir)
                process = subprocess.Popen(['git', 'pull'], env=os.environ,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
                result = []
                while process.poll is None:
                    result.extend(process.stdin.readlines())
                    result.extend(process.stderr.readlines())

                subprocess.Popen(
                    ['touch', FUNNEL_STAGING_TOUCHFILE], env=os.environ,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                os.chdir(savedir) # Is this really required?
                return '\r\n'.join(result)
    else:
        return "Unknown repository, or no access"

application = app # For WSGI

if __name__ == '__main__':
    app.run('0.0.0.0')
