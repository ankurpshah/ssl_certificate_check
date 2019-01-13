import OpenSSL
import ssl, socket
import os
import json
import requests
import time
from datetime import datetime

TODAY = datetime.utcnow()

ALERT_DAYS = int(os.environ.get('ALERT_DAYS'))
SLACK_USER_NAME = os.environ.get('SLACK_USER_NAME')
SLACK_CHANNEL_NAME = os.environ.get('SLACK_CHANNEL_NAME')
SLACK_WEB_HOOK = os.environ.get('SLACK_WEB_HOOK')
DOMAIN_LIST = os.environ.get('DOMAIN_LIST')


def get_certificate(domain_name):
    ctx = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
    ctx.set_options(OpenSSL.SSL.OP_NO_SSLv2)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection = OpenSSL.SSL.Connection(ctx, s)
    connection.connect((domain_name, 443))
    connection.set_tlsext_host_name(domain_name.encode('utf-8'))
    connection.setblocking(1)
    connection.do_handshake()
    cert = connection.get_peer_certificate()
    return cert


def get_certificate_expiry_date(domain_name):
    cert = get_certificate(domain_name)
    expiry_str = cert.get_notAfter().decode('ascii')
    expiry_date = datetime.strptime(expiry_str, '%Y%m%d%H%M%SZ')
    return expiry_date


def get_days_from_today(expiry_date):
    delta = expiry_date - TODAY
    return delta.days


def get_domain_name(domain_name):
    tldlist = domain_name.split(".")
    domain_name_only = ".".join(tldlist[-2:])
    return domain_name_only


def send_slack_message(domains, color, text):
    filed_list = []
    filed_list.append({"title": "Domain Name", "value": "", "short": True})
    filed_list.append({"title": "Expiry Date (in days)", "value": "", "short": True})
    for domain_info in domains:
        filed_list.append({"title": "", "value": domain_info["domain_name"], "short": True})
        filed_list.append({"title": "", "value": str(domain_info["expiry_date"]) + " (" + str(
            domain_info["remaining_days"]) + " days)", "short": True})
    attachment_dict = {}
    attachment_root = dict()
    attachment_dict["title"] = "SSL certificate status"
    attachment_dict["fallback"] = "SSL certificate status"
    attachment_dict["color"] = color
    attachment_dict["text"] = text
    attachment_dict["ts"] = time.time()
    attachment_dict["fields"] = filed_list
    attachment_root["attachments"] = [attachment_dict]
    attachment_root["channel"] = SLACK_CHANNEL_NAME
    attachment_root["username"] = SLACK_USER_NAME
    json_data = json.JSONDecoder().decode(json.dumps(attachment_root))
    requests.post(SLACK_WEB_HOOK, json.dumps(json_data), headers={'content-type': 'application/json'}, verify=False)


def main(event, context):
    alert_certs = []
    normal_certs = []
    domains = DOMAIN_LIST
    domain_list = domains.split(",")
    for domain in domain_list:
        domain_info = {}
        expiry_date = get_certificate_expiry_date(domain)
        remaining_days = get_days_from_today(expiry_date)
        domain_info["expiry_date"] = expiry_date
        domain_info["remaining_days"] = remaining_days
        domain_info["domain_name"] = get_domain_name(domain)
        if remaining_days <= ALERT_DAYS:
            alert_certs.append(domain_info)
        else:
            normal_certs.append(domain_info)

    if len(alert_certs) > 0:
        print(alert_certs)
        send_slack_message(alert_certs, "#ff0000", "SSL certificates expiring in next 30 days")
    if len(normal_certs) > 0:
        print(normal_certs)
        send_slack_message(normal_certs, "#00ff00", "SSL Certificate Expiry Dates")

    response = {"statusCode": 200}
    return response
