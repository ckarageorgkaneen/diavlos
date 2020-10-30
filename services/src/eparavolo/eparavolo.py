#!/usr/bin/env python3
import yaml
import datetime
import zeep

from zeep.wsse.username import UsernameToken

from services.data import IN_FILES


def _request_data(code):
    return {
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

class eParavolo:

    WSDL_URL = 'https://test.gsis.gr/esbpilot/eparavoloPublicService?wsdl'

    class Error:
        NOT_FOUND = {
            'message': 'Δεν βρέθηκαν αποτελέσματα.',
            'code': 404
        }

    def __init__(self):
        self.__client = None

    @property
    def _client(self):
        if self.__client is None:
            with open(IN_FILES['eparavolo_credentials']) as file:
                credentials = yaml.load(file, Loader=yaml.FullLoader)
            self.__client = zeep.Client(wsdl=self.WSDL_URL,
                                        wsse=UsernameToken(
                                            credentials['username'],
                                            credentials['password']))
        return self.__client

    def fetch(self, code):
        response_obj = self._client.service.getParavoloTypeInfo(
            **_request_data(code))
        output_record_obj = response_obj.getParavoloTypeInfoOutputRecord
        if output_record_obj is None:
            success, result = False, self.Error.NOT_FOUND
        else:
            response_dict = zeep.helpers.serialize_object(output_record_obj)
            response_dict['price'] = int(response_dict['price'])
            success, result = True, response_dict
        return success, result
