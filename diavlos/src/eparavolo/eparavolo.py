"""A module for fetching eparavolo API information."""
import datetime
import functools
import logging
import requests
import yaml
import zeep

from zeep.wsse.username import UsernameToken

from zeep.exceptions import Error as ZeepError

from .error import eParavoloErrorCode as ErrorCode
from diavlos.data import IN_FILES

logger = logging.getLogger(__name__)


class eParavoloError(Exception):
    """eParavoloError exception"""


def _error(message):
    logger.error(message)
    raise eParavoloError(message)


def _handle_zeep_error(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except (ZeepError, requests.exceptions.HTTPError) as e:
            _error(str(e))
    return wrapper


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

    _WSDL_URL = 'https://test.gsis.gr/esbpilot/eparavoloPublicService?wsdl'

    def __init__(self):
        self.__client = None

    @property
    def _client(self):
        if self.__client is None:
            with open(IN_FILES['eparavolo_credentials']) as file:
                credentials = yaml.load(file, Loader=yaml.FullLoader)
            self.__client = self._zeep_client(credentials['username'],
                                              credentials['password'])
        return self.__client

    @_handle_zeep_error
    def _zeep_client(self, username, password):
        return zeep.Client(wsdl=self._WSDL_URL,
                           wsse=UsernameToken(
                               username,
                               password))

    @_handle_zeep_error
    def _type_info_output_record(self, code):
        return self._client.service.getParavoloTypeInfo(
            **_request_data(code)).getParavoloTypeInfoOutputRecord

    def fetch(self, code):
        """Fetch eparavolo information by code.

        Args:
            code (int): The eparavolo public service API code, e.g. 7206.

        Returns:
            :obj:`enum 'eParavoloErrorCode'`: A eParavoloErrorCode.NOT_FOUND
                enum, if a paravolo for the code is not found.
            dict: eparavolo information containing description and price,
                e.g. {"description": "Οδικά οχήματα", "price": 177}.
        """
        type_info_output_record = self._type_info_output_record(code)
        if type_info_output_record is None:
            result = ErrorCode.NOT_FOUND
        else:
            response_dict = zeep.helpers.serialize_object(
                type_info_output_record)
            response_dict['price'] = float(response_dict['price'])
            result = response_dict
        return result
