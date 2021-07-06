"""A module for fetching diaugeia API information."""

import logging
import requests

from .error import DiaugeiaErrorCode as ErrorCode

logger = logging.getLogger(__name__)

API_BASE_URL = "https://diavgeia.gov.gr/opendata"
API_TEST_URL = "https://test3.diavgeia.gov.gr/luminapi/opendata/decisions/"


class DiaugeiaError(Exception):
    """diaugeiaError exception"""


def _error(message):
    logger.error(message)
    raise DiaugeiaError(message)


def _request_data(code):
    try:
        r = requests.get(API_TEST_URL + code + '.json')
        result = r.json()

        if 'errors' in result:
            return None
        else:
            return result

    except ConnectionError:
        return None


class Diaugeia:

    def fetch(self, code):
        """Fetch ada information by code from diaugeia API.

            Args:
                code (string): The ada  code, e.g. ΒΛΕΖΝ-Ρ7Ν.

            Returns:
                :obj:`enum 'DiaugeiaErrorCode'`: A DiaugeiaErrorCode.NOT_FOUND
                    enum, if an ada for the code is not found.
                dict: ada information
        """
        response_dict = _request_data(code)
        if response_dict is None:
            result = ErrorCode.NOT_FOUND
        else:
            result = response_dict

        return result
