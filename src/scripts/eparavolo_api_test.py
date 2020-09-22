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

def get_paravolo(code):
    request_data = {
        'auditRecord': {
            'auditTransactionId': ' ',
            'auditTransactionDate': datetime.datetime.now(
            ).strftime("%Y-%m-%dT%H:%M:%SZ"),
            'auditUnit': ' ',
            'auditProtocol': ' ',
            'auditUserId': ' ',
            'auditUserIp': ' ',
        },
        'getParavoloTypeInfoInputRecord': {
            'typeId': code,
            'languageId': 1,
        }
    }
    response_obj = client.service.getParavoloTypeInfo(**request_data)
    output_record_obj = response_obj.getParavoloTypeInfoOutputRecord
    if output_record_obj is None:
        return None
    response_dict = zeep.helpers.serialize_object(output_record_obj)
    response_dict['price'] = int(response_dict['price'])
    return response_dict

response = get_paravolo(123)
print(type(response))
print(response)

