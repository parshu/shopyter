from __future__ import with_statement
from fabric.api import put, env, sudo, roles, run, local, lcd, settings, cd, get
import time

env.roledefs = {
    'box': ['ubuntu@klipiter.com'],
}

env.code_path = '.'
env.deploy_path = './knopon'

@roles('box')
def deploy():
    local('tar -zcvf deploy.tgz batch js backend app siteassets feedserver.py feedserver_restart.sh restart.sh bootstrap jquery-ui-1.8.21.custom templates tools main.py requirements.*')
    put ('deploy.tgz', env.code_path)
    run('tar -C %s -zxvf %s/deploy.tgz' % (env.deploy_path, env.code_path))

def _run_background(command):
    return run('dtach -n `mktemp -u /tmp/dtach.XXXX` %s' % command)

@roles('box')
def restart():
    with settings(warn_only=True):
        run('ps ax | grep python | grep main | grep -v grep | awk {\'print $1\'} | xargs kill')
    with cd(env.deploy_path):
        _run_background('python main.py >> forever.log 2>&1')
    with settings(warn_only=True):
        run('ps ax | grep python | grep feedserver | grep -v grep | awk {\'print $1\'} | xargs kill')
    with cd(env.deploy_path):
        _run_background('python feedserver.py >> feed_forever.log 2>&1')

@roles('box')
def importdb():
    run('/home/ubuntu/downloads/mongodb-linux-x86_64-2.0.4/bin/mongodump')
    run('tar -zcvf dump.tz dump/')
    get('dump.tz', env.code_path)
    local('tar -zxvf dump.tz')
    local('mongorestore')

@roles('box')
def exportdb():
    local('mongodump')
    local('tar -zcvf dump.tz dump/')
    put('dump.tz', env.code_path)
    run('tar -zxvf dump.tz')
    run('/home/ubuntu/downloads/mongodb-linux-x86_64-2.0.4/bin/mongorestore')
