#!/usr/bin/env python
import os, os.path
import json
import subprocess
from flask import Flask, request, redirect, abort
app = Flask(__name__)

GITROOT = '/var/git/github'

@app.route('/')
def index():
    return redirect('http://github.com/hasgeek/doctypehtml5')

@app.route('/', methods=['POST'])
def commit():
    payload = request.form.get('payload')
    if not payload:
        return "Missing form variable 'payload'"
    payload = json.loads(payload)
    reponame = payload['repository']['name']
    savedir = os.getcwd()
    repodir = os.path.join(GITROOT, reponame)
    if os.access(repodir, os.W_OK | os.X_OK):
        os.chdir(repodir)
        process = subprocess.Popen(['git', 'pull'], env=os.environ,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        result = []
        while process.poll is None:
            result.extend(process.stdin.readlines())
            result.extend(process.stderr.readlines())
        os.chdir(savedir) # Is this really required?
        return '\r\n'.join(result)
    else:
        return "Unknown repository, or no access"

application = app # For WSGI

if __name__ == '__main__':
    app.run('0.0.0.0')
