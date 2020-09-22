#!/usr/bin/env python3
import yaml
import datetime
import zeep

from zeep.wsse.username import UsernameToken

with open('eparavolo_credentials.yaml') as file:
    credentials = yaml.load(file, Loader=yaml.FullLoader)

wsdl = 'https://test.gsis.gr/esbpilot/eparavoloPublicService?wsdl'
client = zeep.Client(wsdl=wsdl,
                     wsse=UsernameToken(
                         credentials['username'],
                         credentials['password']))

request_data = {
    'auditRecord': {
        'auditTransactionId': ' ',
        'auditTransactionDate': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        'auditUnit': ' ',
        'auditProtocol': ' ',
        'auditUserId': ' ',
        'auditUserIp': ' ',
    },
    'fetchAllInputRecord': {
        'languageId': 1,
    }
}

response = client.service.fetchAll(**request_data)
print(response)
