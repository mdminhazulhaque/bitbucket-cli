#!/usr/bin/python3

__author__ = "Md. Minhazul Haque"
__version__ = "0.1.0"
__license__ = "GPLv3"

"""
Copyright (c) 2020 Md. Minhazul Haque
This file is part of mdminhazulhaque/bitbucket-cli
(see https://github.com/mdminhazulhaque/bitbucket-cli).
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import click
import requests
import json
import os

BITBUCKET_AUTH = os.environ.get('BITBUCKET_AUTH', None)

if not BITBUCKET_AUTH:
    print('BITBUCKET_AUTH not found in environment')
    print('Genrate app password from the following URL')
    print('https://bitbucket.org/account/settings/app-passwords/')
    exit(1)
else:
    username, password = BITBUCKET_AUTH.split(":")
    BITBUCKET_AUTH = (username, password)

BITBUCKET_API_HEADER = {'Content-Type': "application/json"}
BITBUCKET_BASEURL = "https://api.bitbucket.org/2.0/repositories"
    
def bitbucket_api(endpoint, data=None):
    target = BITBUCKET_BASEURL + endpoint
    if data:
        response = requests.post(target,
                                 headers=BITBUCKET_API_HEADER,
                                 auth=BITBUCKET_AUTH,
                                 json=data)
    else:
        response = requests.get(target,
                                headers=BITBUCKET_API_HEADER,
                                auth=BITBUCKET_AUTH)
    return response.json()

@click.group()
def app():
    pass

@app.command(help="List repositories from a workspace")
@click.option('--workspace', '-w', type=click.STRING, required=True)
def repos(workspace):
    page = 1
    while True:
        endpoint = F"/{workspace}?sort=-updated_on&page={page}"
        data = bitbucket_api(endpoint)
        for repo in data['values']:
            print(repo['name'])
        if 'next' in data:
            page += 1
        else:
            break

@app.command(help="List branches from a repository")
@click.option('--workspace', '-w', type=click.STRING, required=True)
@click.option('--repo', '-r', type=click.STRING, required=True)
def branches(workspace, repo):
    endpoint = F"/{workspace}/{repo}/refs"
    while True:
        data = bitbucket_api(endpoint)
        for repo in data['values']:
            print(repo['name'])
        if 'next' in data:
            endpoint = data['next']
        else:
            break

@app.command(help="List commits from a repository")
@click.option('--workspace', '-w', type=click.STRING, required=True)
@click.option('--repo', '-r', type=click.STRING, required=True)
@click.option('--branch', '-b', type=click.STRING, required=False, default='master')
@click.option('--all', '-a', type=click.BOOL, required=False, default=False)
def commits(workspace, repo, branch, all):
    endpoint = F"/{workspace}/{repo}/commits/{branch}"
    while True:
        data = bitbucket_api(endpoint)
        for commit in data['values']:
            print(commit['hash'], commit['date'], commit['message'].split("\n")[0])
        if not all:
            break
        elif 'next' in data:
            endpoint = data['next']
        else:
            break

@app.command(help="List builds from a repository")
@click.option('--workspace', '-w', type=click.STRING, required=True)
@click.option('--repo', '-r', type=click.STRING, required=True)
@click.option('--all', '-a', type=click.BOOL, required=False)
def builds(workspace, repo, all):
    endpoint = F"/{workspace}/{repo}/pipelines/?sort=-created_on"
    while True:
        data = bitbucket_api(endpoint)
        for pipeline in data['values']:
            print(pipeline['created_on'],
                  pipeline['target']['selector']['pattern'],
                  pipeline['creator']['display_name'])
        if not all:
            break
        elif 'next' in data:
            endpoint = data['next']
        else:
            break

@app.command(help="Trigger pipeline for a branch or commit")
@click.pass_context
@click.option('--workspace', '-w', type=click.STRING, required=True)
@click.option('--repo', '-r', type=click.STRING, required=True)
@click.option('--branch', '-b', type=click.STRING, required=True)
@click.option('--commit', '-c', type=click.STRING, required=False)
@click.option('--pattern', '-p', type=click.STRING, required=False)
def trigger(ctx, workspace, repo, branch, commit, pattern):
    endpoint = F"/{workspace}/{repo}/pipelines/"
    if branch:
        data = {
            "target": {
                "ref_type": "branch",
                "type": "pipeline_ref_target",
                "ref_name": branch
            }
        }
    if commit and pattern:
        data = {
            "target":{
                "commit":{
                    "hash": commit,
                    "type":"commit"
                },
                "selector":{
                    "type":"custom",
                    "pattern": pattern
                },
                "type":"pipeline_ref_target",
                "ref_type":"branch",
                "ref_name": branch
            }
        }
    try:
        response = bitbucket_api(endpoint, data)
        build_number = response['build_number']
        print(F"Pipeline {build_number} started. Click the following URL to see progress.")
        print(F"https://bitbucket.org/{workspace}/{repo}/addon/pipelines/home#!/results/{build_number}")
    except:
        print("Failed")
        exit(1)

@app.command(help="Pipeline variables")
@click.option('--workspace', '-w', type=click.STRING, required=True)
@click.option('--repo', '-r', type=click.STRING, required=True)
@click.option('--create', '-c', type=click.BOOL, is_flag=True)
@click.option('--key', '-k', type=click.STRING, required=False)
@click.option('--value', '-v', type=click.STRING, required=False)
@click.option('--secured', '-s', type=click.BOOL, is_flag=True)
@click.option('--delete', '-d', type=click.STRING, help="UUID of the variable to delete")
def variables(workspace, repo, create, key, value, secured, delete):
    endpoint = F"/{workspace}/{repo}/pipelines_config/variables/"
    if create:
        data = {
            "key": key,
            "value": value
        }
        data['secured'] = True if secured else False
        response = bitbucket_api(endpoint, data)
        print(F"Created {response['uuid']}")
    elif delete:
        params = (
            ('username', workspace),
            ('repo_slug', repo),
            ('variable_uuid', delete)
        )
        endpoint = F"{BITBUCKET_BASEURL}/{workspace}/{repo}/pipelines_config/variables/{delete}"
        response = requests.delete(endpoint,
                                   params=params,
                                   headers=BITBUCKET_API_HEADER,
                                   auth=BITBUCKET_AUTH)
        if response.status_code != 204:
            print("Failed")
            exit(1)
    else:
        response = bitbucket_api(endpoint)
        for variable in response['values']:
            uuid = variable['uuid']
            key = variable['key']
            value = "*"*20 if variable['secured'] else variable['value']
            print(uuid, key, value)

if __name__ == "__main__":
    app()
