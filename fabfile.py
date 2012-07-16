from __future__ import with_statement
from fabric.api import put, env, sudo, roles, run, local, lcd, settings, cd, get
import time

env.roledefs = {
    'box': ['ubuntu@ec2-50-18-129-86.us-west-1.compute.amazonaws.com'],
}

env.code_path = '.'
env.deploy_path = './knopon'

@roles('box')
def deploy():
    local('tar -zcvf deploy.tgz batch app siteassets bootstrap jquery-ui-1.8.21.custom templates tools main.py requirements.*')
    put ('deploy.tgz', env.code_path)
    run('tar -C %s -zxvf %s/deploy.tgz' % (env.deploy_path, env.code_path))

def _run_background(command):
    return run('dtach -n `mktemp -u /tmp/dtach.XXXX` %s' % command)

@roles('box')
def restart():
    with settings(warn_only=True):
        run('ps ax | grep python | grep main | grep -v grep | awk {\'print $1\'} | xargs kill')
    with cd(env.deploy_path):
        _run_background('python main.py >>forever.log 2>&1')

@roles('box')
def importdb():
    run('/home/ubuntu/downloads/mongodb-linux-x86_64-2.0.4/bin/mongodump')
    run('tar -zcvf dump.tz dump/')
    get('dump.tz', env.code_path)
    local('tar -zxvf dump.tz')
    local('mongorestore')
