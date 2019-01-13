# ssl_certificate_check
Check Certificate expiration and notify to Slack using Kubeless

## Pre-requisite
* [Serverless](https://serverless.com/) framework must be installed.
* [Kubernetes](https://kubernetes.io/) cluster
* [Kubeless](https://kubeless.io/) must be installed in existing kubernetes cluster.

## Installation
* Run one of following command to install `serverless-kubeless` plugin.
```bash
npm install -g serverless-kubeless

```
or
```bash
sls plugin install -n serverless-kubeless

```

## Configuration
* To adding multiple domain for SSL certificate check, add domain exactly in `DOMAIN_LIST` envrionment variable in `serverless.yml`. (comma seperated) for e.g.:
```.env
DOMAIN_LIST="ankurpshah.com,example.com"
```
* Configure appropriate `SLACK_WEB_HOOK` URL and `SLACK_CHANNEL_NAME` in `serverless.yml` file.

## Deployment
* Run following command 
```bash
sls deploy
```
