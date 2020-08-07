# Bitbucket-CLI

Interact with your Bitbucket repositories over CLI

## Motivation

As a DevOps, I have to check Bitbucket branches, commits and pipelines frequently. It is a real pain in the /dev/urandom to open Bitbucket and browse pages for the desired information. So I wrote a small tool that can help me to list branches, commits, builds etc. Also this tool helped me to trigger custom pipelines on certain commits across multiple repositories.

## App Password

The tool uses Bitbucket App Password for authentication. Generate one from [here](https://bitbucket.org/account/settings/app-passwords/). Make sure the following permissions are set otherwise the API calls will fail.

- [x] Workspace *Read*
- [x] Repositories *Read*
- [x] Pipelines *Read*
- [x] Pipelines *Write* (If you want to trigger new one)
- [x] Pipelines *Edit variables* (If you want to amend environments)

Once you generate one, export it as `BITBUCKET_AUTH` similar to `cURL`'s BasicAuthentication.

```bash
$ export BITBUCKET_AUTH=mdminhazulhaque:CnxnwA104TRuW4LVyw6ew
```

## API?

The utility uses official [Bitbucket REST API](https://developer.atlassian.com/bitbucket/api/2/reference/resource/)

## Synopsis

### List Repositories

```bash
$ bitbucket-cli list -w myworkspace
frontend-v2
frontend-v1
awesome-api
awesome-api-doc
blog
playbooks
```

### List Branches

```bash
$ bitbucket-cli branches -w myworkspace -r frontend-v2
master
staging
develop
FE1-bugfix-prod
FE1-api-issue
```

### List Commits

```bash
$ bitbucket-cli commits -w myworkspace -r blog
bd4ed959e90944d8f661de57d314dd8eacd5e79e 2019-11-21T11:58:13+00:00 Merge branch 'staging'
c06210ce46cf00a24724f70265ab57c5dd1431bf 2020-05-21T18:28:03+00:00 wp-config.php edited online with Bitbucket
b60f0381e2b2571af6c573899e9870793237c5c4 2020-01-10T01:09:36+00:00 Merged in fix-theme-padding (pull request #31)
a84de9d65d8e54589e4a3901b20e65c557a42df7 2020-01-10T01:08:50+00:00 Merged in fix-widget-issue (pull request #30)
5da48ff3d75b4911fb5b20a07045a5ac39680ae2 2019-11-21T11:57:05+00:00 Merge branch 'develop' into staging
```

### List Builds

```bash
$ bitbucket-cli builds -w myworkspace -r blog
2020-07-24T03:56:07.704Z master Md Minhazul Haque
2020-07-23T06:19:35.715Z staging Foo Bob
2020-07-06T01:52:33.846Z develop Alice Bar
```

### Trigger Pipeline on Branch

```bash
$ bitbucket-cli trigger -w myworkspace -r blog -b master
Pipeline 69 started. Click the following URL to see progress.
https://bitbucket.org/myworkspace/blog/addon/pipelines/home#!/results/69
```

### Trigger Custom Pipeline on Commit

```bash
$ bitbucket-cli trigger -w myworkspace -r blog -b master -c 5da48ff3d75b4911fb5b20a07045a5ac39680ae2 -p deploy-prod
Pipeline 69 started. Click the following URL to see progress.
https://bitbucket.org/myworkspace/blog/addon/pipelines/home#!/results/69
```

### List Repository Variables

```bash
$ bitbucket-cli variables -w myworkspace -r blog
{8cc198d9-44ff-43ea-9473-acd697bcbf31} AWS_ACCESS_KEY_ID AKIA123456789123456789Z
{9f06955b-3ca9-4b93-908f-fe353977ec48} AWS_SECRET_ACCESS_KEY ********************
{18643776-dbe1-4fe6-b01b-6d103242c9ca} AWS_DEFAULT_REGION ap-southeast-1
{03926d83-d133-474b-bd6c-bdd0b3fb73c4} DEV_WORDPRESS_DB_HOST prod.lsoeiwxbjse.ap-southeast-1.rds.amazonaws.com:3306
{142c6bfb-8500-44e7-9861-2deb93d40a1a} DEV_WORDPRESS_DB_NAME wordpress
{937f2270-c6ea-455e-9b63-e9871c4cb3c7} DEV_WORDPRESS_DB_PASSWORD ********************
{c2b7cb98-cc3b-4294-82d8-fddb9f187621} DEV_WORDPRESS_DB_USER admin
{03834927-66b2-45a5-a595-8b92ce508ab8} DEV_WORDPRESS_TABLE_PREFIX wp_
```

### Add Repository Variable

> Use `-s` to set variable to secure!

```bash
$ bitbucket-cli variables -w myworkspace -r blog -c -k AWS_ACCESS_KEY_ID -v AKIA123456789123456789Z
Created {b127caae-2493-4e01-b878-6a8b8b4400a7}
$ bitbucket-cli variables -w myworkspace -r blog -c -k AWS_SECRET_ACCESS_KEY -v AZea5a73d89faa1d0ddbd7cbe41961a4d0392bd13d886b7045f -s
Created {b127caae-2493-4e01-b878-6a8b8b4400a7}
```

### Delete Repository Variable

> Bitbucket UUID are always enclosed with curly braces!

```bash
$ bitbucket-cli variables -w myworkspace -r blog -d '{b127caae-2493-4e01-b878-6a8b8b4400a7}'
```

## TODO

- [ ] SSH key, Host signature management
- [ ] Create, List, Approve, Reject PR
- [ ] Add/Remove Branch permissions
